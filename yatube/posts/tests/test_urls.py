from http import HTTPStatus

from django.test import TestCase, Client
from django.urls import reverse

from ..models import Group, Post, User


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_user')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст',
            group=cls.group,
        )
        cls.urls_authorized = {
            f'/posts/{cls.post.pk}/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html',
            '/follow/': 'posts/follow.html',
            f'/profile/{cls.user}/follow/': 'posts/follow.html',
            f'/profile/{cls.user}/unfollow/': 'posts/index.html',
        }
        cls.urls_guest = {
            '/': 'posts/index.html',
            '/about/tech/': 'about/tech.html',
            '/about/author/': 'about/author.html',
            f'/group/{cls.group.slug}/': 'posts/group_list.html',
            f'/profile/{cls.user}/': 'posts/profile.html',
            f'/posts/{cls.post.pk}/': 'posts/post_detail.html',
        }

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_urls_exist_at_desired_location_guest(self):
        """Главная, страницы "Об авторе" и "Технологии", страница группы,
        профиль пользователя и страница подробной информации о посте
        доступны любому пользователю."""
        for page in self.urls_guest:
            with self.subTest(page=page):
                response = self.guest_client.get(page)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_create_edit_urls_exists_at_desired_location_authorized(self):
        """Страницы /edit, /create, /follow, username/follow,
        username/unfollow доступны авторизованному пользователю."""
        for page in self.urls_authorized:
            with self.subTest(page=page):
                response = self.authorized_client.get(page)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_create_edit_urls_redirect_guest(self):
        """Неавторизованный пользователь получает редирект со страниц /edit,
        /create, /follow, username/follow, username/unfollow."""
        for page in self.urls_authorized:
            with self.subTest(page=page):
                response = self.guest_client.get(page)
                self.assertRedirects(response,
                                     reverse('users:login') + f'?next={page}')

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for url, template in self.urls_guest.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertTemplateUsed(response, template)
        all_urls = {**self.urls_guest, **self.urls_authorized}
        for url, template in all_urls.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_unexisting_page(self):
        """Несуществующая страница возвращает ошибку 404 и использует шаблон
        404.html. """
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTemplateUsed(response, 'core/404.html')
