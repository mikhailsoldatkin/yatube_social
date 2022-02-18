import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client, override_settings
from django.urls import reverse

from ..models import Post, User, Group, Comment, Follow

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_user')
        cls.user_author = User.objects.create_user(username='test_author')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.another_group = Group.objects.create(
            title='Другая группа',
            slug='another-slug',
            description='Другое описание',
        )
        cls.post_image = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='post_image.gif',
            content=cls.post_image,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тест форм',
            group=cls.group,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_post_create(self):
        """Валидная форма создает пост в базе данных."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Текст создаваемого поста',
            'group': self.group.pk,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('posts:profile', kwargs={
            'username': self.user}))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        last_created_post = Post.objects.latest('pub_date')
        self.assertEqual(last_created_post.text, form_data['text'])
        self.assertEqual(last_created_post.group.pk, form_data['group'])
        self.assertEqual(last_created_post.author, self.user)

    def test_post_edit(self):
        """Валидная форма редактирует пост."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Редактируемый текст',
            'group': self.another_group.pk,
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={
                'post_id': self.post.pk}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('posts:post_detail', kwargs={
            'post_id': self.post.pk}))
        self.assertEqual(Post.objects.count(), posts_count)
        edited_post = Post.objects.get(id=self.post.pk)
        self.assertEqual(edited_post.text, form_data['text'])
        self.assertEqual(edited_post.group.pk, form_data['group'])
        response_group = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': self.group.slug}))
        self.assertNotIn(edited_post, response_group.context['page_obj'])

    def test_guest_cant_create_post(self):
        """Неавторизованный пользователь не может создать пост."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Текст поста',
            'group': self.group.pk
        }
        response = self.guest_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response,
                             reverse('users:login') + '?next=/create/')
        self.assertEqual(Post.objects.count(), posts_count)

    def test_create_post_with_image(self):
        """Валидная форма создает пост с картинкой в базе данных."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Текст создаваемого поста',
            'group': self.group.pk,
            'image': self.uploaded
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('posts:profile', kwargs={
            'username': self.user}))
        self.assertEqual(Post.objects.count(), posts_count + 1)
        last_created_post = Post.objects.latest('pub_date')
        self.assertEqual(last_created_post.text, form_data['text'])
        self.assertEqual(last_created_post.group.pk, form_data['group'])
        self.assertEqual(last_created_post.image,
                         f'posts/{form_data["image"]}')

    def test_authorized_can_leave_comments(self):
        """Авторизованный пользователь может оставлять комментарии."""
        comments_count = Comment.objects.count()
        form_data = {
            'text': 'Текст комментария',
        }
        response = self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.pk}),
            data=form_data,
            follow=True
        )
        last_comment = Comment.objects.latest('created')
        self.assertRedirects(response, reverse('posts:post_detail', kwargs={
            'post_id': self.post.pk}))
        self.assertEqual(Comment.objects.count(), comments_count + 1)
        self.assertEqual(last_comment.text, form_data['text'])

    def test_guest_cant_leave_comments(self):
        """Неавторизованный пользователь не может оставлять комментарии."""
        comments_count = Comment.objects.count()
        form_data = {
            'text': 'Текст комментария',
        }
        response = self.guest_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.pk}),
            data=form_data,
            follow=True
        )
        self.assertEqual(Comment.objects.count(), comments_count)
        self.assertRedirects(response, reverse(
            'users:login') + f'?next=/posts/{self.post.pk}/comment/')

    def test_authorized_user_can_subscribe_to_another_user(self):
        """Авторизованный пользователь может подписываться на других
        пользователей и отписываться от них."""
        author = self.user_author
        user = self.user
        count_followers = author.following.count()
        self.authorized_client.get(
            reverse('posts:profile_follow', kwargs={'username': author}))
        self.assertEqual(author.following.count(), count_followers + 1)
        self.assertTrue(
            Follow.objects.filter(user=user, author=author).exists())
        count_followers = author.following.count()
        self.authorized_client.get(
            reverse('posts:profile_unfollow', kwargs={'username': author}))
        self.assertEqual(author.following.count(), count_followers - 1)
        self.assertFalse(
            Follow.objects.filter(user=user, author=author).exists())

    def test_guest_user_cant_subscribe_to_another_user(self):
        """Неавторизованный пользователь не может подписываться на других
        пользователей."""
        author = self.user_author
        count_followers = author.following.count()
        response = self.guest_client.get(
            reverse('posts:profile_follow', kwargs={'username': author}))
        self.assertEqual(author.following.count(), count_followers)
        self.assertRedirects(response, reverse(
            'users:login') + f'?next=/profile/{author}/follow/')
