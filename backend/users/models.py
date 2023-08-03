from django.contrib.auth.models import AbstractUser
from django.db import models
from users.validators import validate_username


class User(AbstractUser):
    email = models.EmailField(
        max_length=254,
        verbose_name='Электронная почта',
        unique=True,
        blank=True,
    )
    username = models.CharField(
        max_length=150,
        verbose_name='Никнейм',
        validators=[validate_username],
        blank=True,
        unique=True,
    )
    first_name = models.CharField(
        max_length=150,
        verbose_name='Имя',
        blank=True,
    )
    last_name = models.CharField(
        max_length=150,
        verbose_name='Фамилия',
        blank=True,
    )
    password = models.CharField(
        max_length=150,
        verbose_name='Пароль',
        blank=True,
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        null=True,
    )
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        null=True,
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'