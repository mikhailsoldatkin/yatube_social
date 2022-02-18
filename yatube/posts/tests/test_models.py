from django.test import TestCase

from ..models import Group, Post, User, Comment, Follow


class PostModelTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_user')
        cls.user_author = User.objects.create_user(username='test_author')
        cls.group = Group.objects.create(
            title='Название тестовой группы',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст для проверки',
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            text='Текст комментария'
        )
        cls.follow = Follow.objects.create(
            user=cls.user,
            author=cls.user_author,
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        post = PostModelTests.post
        group = PostModelTests.group
        expected_values_models = {
            post: post.text[:15],
            group: group.title,
        }
        for model, expected_value in expected_values_models.items():
            with self.subTest(model=model):
                self.assertEqual(expected_value, str(model))

    def test_help_text(self):
        """Проверяем, что help_text в полях моделей совпадает с ожидаемым."""
        post = PostModelTests.post
        field_help_texts = {
            'text': 'Введите текст поста',
            'group': 'В какую группу публикуем?',
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).help_text, expected_value)

    def test_verbose_names_post(self):
        """Проверяем, что verbose_name полей модели Post совпадает с
        ожидаемым."""
        post = PostModelTests.post
        field_verbose_name = {
            'text': 'Текст',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'group': 'Группа',
        }
        for field, expected_value in field_verbose_name.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).verbose_name, expected_value)

    def test_verbose_names_group(self):
        """Проверяем, что verbose_name полей модели Group совпадает с
        ожидаемым."""
        group = PostModelTests.group
        field_verbose_name = {
            'title': 'Название',
            'slug': 'Адрес',
            'description': 'Описание',
        }
        for field, expected_value in field_verbose_name.items():
            with self.subTest(field=field):
                self.assertEqual(
                    group._meta.get_field(field).verbose_name, expected_value)

    def test_verbose_names_comment(self):
        """Проверяем, что verbose_name полей модели Comment совпадает с
        ожидаемым."""
        comment = PostModelTests.comment
        field_verbose_name = {
            'post': 'Пост',
            'author': 'Автор',
            'text': 'Текст комментария',
            'created': 'Дата добавления',
        }
        for field, expected_value in field_verbose_name.items():
            with self.subTest(field=field):
                self.assertEqual(
                    comment._meta.get_field(field).verbose_name,
                    expected_value)

    def test_verbose_names_follow(self):
        """Проверяем, что verbose_name полей модели Follow совпадает с
        ожидаемым."""
        follow = PostModelTests.follow
        field_verbose_name = {
            'user': 'Подписчик',
            'author': 'Автор',
        }
        for field, expected_value in field_verbose_name.items():
            with self.subTest(field=field):
                self.assertEqual(
                    follow._meta.get_field(field).verbose_name,
                    expected_value)
