from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import UniqueConstraint

User = get_user_model()


class Group(models.Model):
    title = models.CharField("Название", max_length=200, default=None)
    slug = models.SlugField("Адрес", max_length=100, unique=True)
    description = models.TextField("Описание", blank=True, null=True)

    def __str__(self):
        return str(self.title)

    class Meta:
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'


class Post(models.Model):
    text = models.TextField("Текст", help_text='Введите текст поста')

    pub_date = models.DateTimeField("Дата публикации", auto_now_add=True,
                                    db_index=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name="Автор",
    )
    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='posts',
        verbose_name="Группа",
        help_text='В какую группу публикуем?'
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )

    def __str__(self):
        return self.text[:15]

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name="Пост",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name="Автор",
    )
    text = models.TextField("Текст комментария",
                            help_text='Напишите комментарий')
    created = models.DateTimeField("Дата добавления", auto_now_add=True)

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        related_name='follower',
        verbose_name="Подписчик",
        on_delete=models.CASCADE,
    )
    author = models.ForeignKey(
        User,
        related_name='following',
        verbose_name="Автор",
        on_delete=models.CASCADE,
    )

    class Meta:
        constraints = [
            UniqueConstraint(fields=['user', 'author'],
                             name='unique_following')
        ]
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
