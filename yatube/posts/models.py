"""Module with models of posts app."""

from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.deletion import PROTECT

User = get_user_model()


class Group(models.Model):
    """Model for group."""

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()

    def __str__(self) -> str:
        """Get string representation of group object."""
        return self.title


class Post(models.Model):
    """Model for post."""

    text = models.TextField(
        verbose_name='Текст поста',
        help_text='Введите текст поста'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор'
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        related_name='posts',
        blank=True,
        null=True,
        verbose_name='Группа',
        help_text='Выберите группу'
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )

    class Meta:
        """Meta-class for post model."""

        ordering = ['-pub_date']

    def __str__(self) -> str:
        """Get string representation of post object."""
        return self.text[:15]


class Comment(models.Model):
    """Model for comment."""

    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Комментарий'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор'
    )
    text = models.TextField(
        verbose_name='Текст комментария',
        help_text='Введите текст комментария'
    )
    created = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True
    )

    class Meta:
        """Meta-class for comment model."""

        ordering = ['-created']

    def __str__(self) -> str:
        """Get string representation of post object."""
        return self.text[:15]


class Follow(models.Model):
    """Model for follow."""

    user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='follower',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User,
        on_delete=PROTECT,
        related_name='following',
        verbose_name='Подписка'
    )

    class Meta:
        """Meta-class for follow model."""

        models.UniqueConstraint(
            fields=['user', 'author'], name='unique_follow')

    def __str__(self) -> str:
        """Get string representation of post object."""
        return f'{self.user} follows {self.author}'
