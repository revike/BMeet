from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """ Пользователь """

    email = models.EmailField(
        unique=True,
    )
    activation_key = models.CharField(
        max_length=128,
        blank=True,
    )
    is_verify = models.BooleanField(
        default=False,
    )

    def __str__(self):
        return f'{self.username} - {self.email}'

    class Meta:
        db_table = "users"
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
