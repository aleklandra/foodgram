from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models


class User(AbstractUser):
    """Пользователи."""
    email = models.EmailField(max_length=254, unique=True)
    username = models.CharField(max_length=150, unique=True)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    avatar = models.ImageField(
        upload_to='user/images/',
        null=True,
        blank=True,
        default=None
    )
    password = models.CharField(max_length=150)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name', 'password']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('email', )

    def __str__(self):
        return f'{self.username}'


class UserSubscription(models.Model):
    person_id = models.ForeignKey(User, on_delete=models.CASCADE,
                                  related_name='user_person')
    sub_id = models.ForeignKey(User, on_delete=models.CASCADE,
                               related_name='user_subscription')

    class Meta:
        verbose_name = 'Подпика'
        verbose_name_plural = 'Подписки'
        ordering = ('sub_id', )

    def __str__(self):
        return f'{self.sub_id}'
