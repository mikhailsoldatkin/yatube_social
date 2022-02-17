import shutil
import tempfile

from django import forms
from django.conf import settings
from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client, override_settings
from django.urls import reverse

from ..forms import PostForm
from ..models import Group, Post, User, Comment, Follow

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostViewsTests(TestCase):
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
            text='Тестовый текст',
            group=cls.group,
            image=cls.uploaded,
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            text='Текст комментария'
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        pages_templates = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list',
                    kwargs={'slug': self.group.slug}): 'posts/group_list.html',
            reverse('posts:profile',
                    kwargs={'username': self.user}): 'posts/profile.html',
            reverse('posts:post_detail', kwargs={
                'post_id': self.post.pk}): 'posts/post_detail.html',
            reverse('posts:post_edit', kwargs={
                'post_id': self.post.pk}): 'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
        }
        for page, template in pages_templates.items():
            with self.subTest(page=page):
                response = self.authorized_client.get(page)
                self.assertTemplateUsed(response, template)

    def test_index_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.guest_client.get(reverse('posts:index'))
        post = response.context.get('page_obj')[0]
        post_author = post.author
        post_text = post.text
        post_group = post.group
        post_pub_date = post.pub_date
        self.assertEqual(post_author, self.post.author)
        self.assertEqual(post_text, self.post.text)
        self.assertEqual(post_group, self.post.group)
        self.assertEqual(post_pub_date, self.post.pub_date)

    def test_group_list_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.guest_client.get(
            reverse('posts:group_list', kwargs={'slug': self.group.slug}))
        post = response.context.get('page_obj')[0]
        self.assertEqual(post, self.post)
        self.assertEqual(response.context['group'], self.post.group)

    def test_profile_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.guest_client.get(
            reverse('posts:profile', kwargs={'username': self.user}))
        post = response.context.get('page_obj')[0]
        self.assertEqual(post, self.post)
        self.assertEqual(response.context['author'], self.post.author)

    def test_post_detail_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.guest_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.pk}))
        self.assertEqual(response.context['post'], self.post)
        self.assertEqual(response.context['posts_count'],
                         self.user.posts.count())

    def test_post_create_show_correct_context(self):
        """Шаблон create_post сформирован с правильным контекстом."""
        responses = [
            self.authorized_client.get(reverse('posts:post_create')),
            self.authorized_client.get(
                reverse('posts:post_edit', kwargs={'post_id': self.post.pk})),
        ]
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for response in responses:
            self.assertIn('form', response.context)
            self.assertIsInstance(response.context['form'], PostForm)
            for value, expected in form_fields.items():
                with self.subTest(value=value):
                    form_field = response.context['form'].fields.get(value)
                    self.assertIsInstance(form_field, expected)
        self.assertIn('is_edit', responses[1].context)
        self.assertIsInstance(responses[1].context['is_edit'], bool)

    def test_created_post_with_group_on_index_page(self):
        """Созданный пост с группой появляется на главной странице сайта"""
        response = self.guest_client.get(reverse('posts:index'))
        self.assertIn(self.post, response.context['page_obj'])

    def test_created_post_with_group_on_group_list(self):
        """Созданный пост с группой появляется на странице группы"""
        response = self.guest_client.get(reverse('posts:group_list', kwargs={
            'slug': self.group.slug}))
        self.assertIn(self.post, response.context['page_obj'])

    def test_created_post_with_group_on_profile(self):
        """Созданный пост с группой появляется на странице профайла автора"""
        response = self.guest_client.get(reverse('posts:profile', kwargs={
            'username': self.user}))
        self.assertIn(self.post, response.context['page_obj'])

    def test_created_post_with_group_not_in_another_group(self):
        """Созданный пост с группой не попал в другую группу"""
        response = self.guest_client.get(reverse('posts:group_list', kwargs={
            'slug': self.group.slug}))
        self.assertIn(self.post, response.context['page_obj'])

    def test_created_post_with_image_is_on_home_page(self):
        """При выводе поста с картинкой на главную страницу изображение
        передаётся в словаре context."""
        response = self.guest_client.get(reverse('posts:index'))
        self.assertEqual(self.post.image,
                         response.context['page_obj'][0].image)

    def test_created_post_with_image_is_on_profile_page(self):
        """При выводе поста с картинкой на страницу профайла изображение
        передаётся в словаре context."""
        response = self.guest_client.get(reverse('posts:profile', kwargs={
            'username': self.user}))
        self.assertEqual(self.post.image,
                         response.context['page_obj'][0].image)

    def test_created_post_with_image_is_on_group_page(self):
        """При выводе поста с картинкой на страницу группы изображение
        передаётся в словаре context."""
        response = self.guest_client.get(reverse('posts:group_list', kwargs={
            'slug': self.group.slug}))
        self.assertEqual(self.post.image,
                         response.context['page_obj'][0].image)

    def test_created_post_with_image_is_on_post_detail_page(self):
        """При выводе поста с картинкой на страницу информации о посте
        изображение передаётся в словаре context."""
        response = self.guest_client.get(reverse('posts:post_detail', kwargs={
            'post_id': self.post.pk}))
        self.assertEqual(self.post.image,
                         response.context['post'].image)

    def test_added_comment_is_on_post_detail_page(self):
        """Оставленный комментарий появляется на странице поста"""
        response = self.guest_client.get(reverse('posts:post_detail', kwargs={
            'post_id': self.post.pk}))
        self.assertIn(self.comment, response.context['comments'])

    def test_index_page_cache(self):
        """Главная страница кэшируется."""
        cache.clear()
        post = Post.objects.get(pk=1)
        self.guest_client.get(reverse('posts:index'))
        cache_index = cache.get(make_template_fragment_key('index_page'))
        post.delete()
        self.guest_client.get(reverse('posts:index'))
        self.assertIn(post.text, cache_index)
        cache.clear()
        self.guest_client.get(reverse('posts:index'))
        cache_index = cache.get(make_template_fragment_key('index_page'))
        self.assertNotIn(post.text, cache_index)

    def test_authorized_user_can_subscribe_to_another_user(self):
        """Авторизованный пользователь может подписываться на других
        пользователей и удалять их из подписок."""
        author = self.user_author
        user = self.user
        count_followers = author.following.count()
        self.authorized_client.get(
            reverse('posts:profile_follow', kwargs={'username': author}))
        self.assertEqual(author.following.count(), count_followers + 1)
        self.assertTrue(
            Follow.objects.filter(user=user, author=self.user_author).exists())
        count_followers = author.following.count()
        self.authorized_client.get(
            reverse('posts:profile_unfollow', kwargs={'username': author}))
        self.assertEqual(author.following.count(), count_followers - 1)
        self.assertFalse(
            Follow.objects.filter(user=user, author=author).exists())

    def test_new_post_is_on_favorites_page(self):
        """Новая запись пользователя появляется в ленте тех, кто на него
        подписан и не появляется в ленте тех, кто не подписан."""
        author = self.user_author
        post = Post.objects.create(text='Проверка подписки',
                                   author=author)
        self.authorized_client.get(
            reverse('posts:profile_follow', kwargs={'username': author}))
        response = self.authorized_client.get(reverse('posts:follow_index'))
        self.assertIn(post, response.context['page_obj'])
        self.authorized_client.get(
            reverse('posts:profile_unfollow', kwargs={'username': author}))
        response = self.authorized_client.get(reverse('posts:follow_index'))
        self.assertNotIn(post, response.context['page_obj'])


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_user')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.POSTS_PER_PAGE = 10

    def setUp(self):
        self.guest_client = Client()
        self.text = 'Текст '
        self.author = self.user
        bulk_list = [
            Post(
                text=self.text + str(i),
                author=self.author,
                group=self.group,
            )
            for i in range(self.POSTS_PER_PAGE + 3)
        ]
        self.posts = Post.objects.bulk_create(bulk_list)

    def test_index_first_page_contains_ten_posts(self):
        """Для главной страницы количество постов на первой странице равно
        10."""
        response = self.guest_client.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page_obj']),
                         self.POSTS_PER_PAGE)

    def test_index_second_page_contains_three_posts(self):
        """Для главной страницы количество постов на второй странице равно
        3."""
        response = self.guest_client.get(reverse('posts:index') + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_group_list_first_page_contains_ten_posts(self):
        """Для страницы группы количество постов на первой странице равно
        10."""
        response = self.guest_client.get(
            reverse('posts:group_list', kwargs={'slug': self.group.slug}))
        self.assertEqual(len(response.context['page_obj']),
                         self.POSTS_PER_PAGE)

    def test_group_list_second_page_contains_three_posts(self):
        """Для страницы группы количество постов на второй странице равно 3."""
        response = self.guest_client.get(reverse('posts:group_list', kwargs={
            'slug': self.group.slug}) + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_profile_first_page_contains_ten_posts(self):
        """Для профайла количество постов на первой странице равно 10."""
        response = self.guest_client.get(
            reverse('posts:profile', kwargs={'username': self.user}))
        self.assertEqual(len(response.context['page_obj']),
                         self.POSTS_PER_PAGE)

    def test_profile_second_page_contains_three_posts(self):
        """Для профайла количество постов на второй странице равно 3."""
        response = self.guest_client.get(reverse('posts:profile', kwargs={
            'username': self.user}) + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)
