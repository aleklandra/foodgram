from django.db import models
from django.contrib.auth.models import AbstractUser, UserManager


class User(AbstractUser):
    """Пользователи."""
    email = models.EmailField(max_length=254, unique=True)
    username = models.CharField(max_length=150, unique=True)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    avatar = models.ImageField(
        upload_to='user/images/',
        null=True,
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


class UserSubscription(models.Model):
    person_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_person')
    sub_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_subscription')
