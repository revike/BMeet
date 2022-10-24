from django.db import models
from django.contrib.auth.models import AbstractUser
from users.validators import username_validate, password_validate
from django.utils.translation import gettext_lazy as _


class LowercaseEmailField(models.EmailField):
    def get_prep_value(self, value):
        return str(value).lower()


class User(AbstractUser):
    """ Пользователь """

    username = models.CharField(
        _("username"), max_length=150, unique=True,
        validators=[username_validate],
        error_messages={
            "unique": _(
                "A user with that username already exists."),
        },
    )

    password = models.CharField(
        _("password"), max_length=128,
        validators=[password_validate],
    )

    email = LowercaseEmailField(
        unique=True,
    )
    activation_key = models.CharField(
        max_length=128,
        blank=True,
    )
    is_verify = models.BooleanField(
        default=False, verbose_name='верифицирован'
    )

    def __str__(self):
        return f'{self.username} - {self.email}'

    class Meta:
        db_table = "users"
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
