from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from ..forms import CreationForm

User = get_user_model()


class UserCreationFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.form = CreationForm()

    def setUp(self):
        self.guest_client = Client()

    def test_users_signup(self):
        """Валидная форма создает нового пользователя в базе данных."""
        users_count = User.objects.count()
        form_data = {
            'first_name': 'Имя',
            'last_name': 'Фамилия',
            'username': 'test_user',
            'email': 'tester@gmail.com',
            'password1': 'test_password',
            'password2': 'test_password'
        }
        response = self.guest_client.post(
            reverse('users:signup'),
            data=form_data,
        )
        self.assertRedirects(response, reverse('posts:index'))
        self.assertEqual(User.objects.count(), users_count + 1)
