import os

from PIL import Image
from django.core.validators import RegexValidator
from django.db import models
from django.contrib.auth.models import AbstractUser

from backend.settings import MEDIA_URL
from users.validators import username_validate, password_validate
from django.utils.translation import gettext_lazy as _


def upload_to(instance, filename=''):
    """Путь хранения аватарок"""
    return ''.join([f'images/user_avatars/{instance.username}/', filename])


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
    friends = models.ManyToManyField(
        "User", blank=True,
        verbose_name='друзья'
    )
    email = LowercaseEmailField(
        unique=True,
    )
    phone_number_regex = RegexValidator(regex=r"^\+7\d{10,10}$",
                                        message='number error')
    phone = models.CharField(validators=[phone_number_regex],
                             error_messages={
                                 "unique": _(
                                     "A user with that phone already exists."),
                             },
                             max_length=12,
                             unique=True, null=True, blank=True,
                             verbose_name='телефон')
    user_photo = models.ImageField(upload_to=upload_to, blank=True,
                                   null=True, verbose_name='аватарка')

    activation_key = models.CharField(
        max_length=128,
        blank=True,
    )
    is_verify = models.BooleanField(
        default=False, verbose_name='верифицирован'
    )

    def save(self, *args, **kwargs):
        if not self.phone:
            self.phone = None
        save_user = super().save(*args, **kwargs)
        path = f'{MEDIA_URL}{upload_to(self)}'
        self.update_photo(path)
        return save_user

    @staticmethod
    def update_photo(path, fixed_width=300):
        try:
            photos = os.listdir(path)
            for photo in photos:
                img = Image.open(f'{path}{photo}')
                width_percent = (fixed_width / float(img.size[0]))
                # img.size[0] - квадратная фотка (кривая)
                height_size = int((float(img.size[1]) * float(width_percent)))
                new_image = img.resize((fixed_width, height_size))
                new_image.save(f'{path}{photo}')
        except FileNotFoundError:
            ...

    def __str__(self):
        return f'{self.username} - {self.email}'

    class Meta:
        db_table = "users"
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"


class TemporaryBanIp(models.Model):
    """Временная блокировка при попытке подбора пароля"""

    ip_address = models.GenericIPAddressField(
        verbose_name='IP адрес',
    )
    attempts = models.IntegerField(
        verbose_name='Неудачных попыток',
        default=0,
    )
    time_unblock = models.DateTimeField(
        verbose_name='Время разблокировки',
        blank=True,
    )
    status = models.BooleanField(
        verbose_name="Статус блокировки",
        default=False
    )

    def __str__(self):
        return f'{self.ip_address} - {self.status}'

    class Meta:
        db_table = "temporary_ban_ip"
        verbose_name = "временная блокировка"
        verbose_name_plural = "временная блокировка"


class FriendRequest(models.Model):
    """Заявка в друзья"""

    from_user = models.ForeignKey(
        User, related_name="from_user",
        on_delete=models.CASCADE,
        verbose_name='от кого',
    )
    to_user = models.ForeignKey(
        User, related_name="to_user",
        on_delete=models.CASCADE,
        verbose_name='кому',
    )
    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name='создана заявка',
    )
    message = models.TextField(
        verbose_name='сообщение',
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='заявка',
    )
    is_except = models.BooleanField(
        default=True,
        verbose_name='принята заявка',
    )

    class Meta:
        db_table = "friend_request"
        verbose_name = "запрос в друзья"
        verbose_name_plural = "запрос в друзья"
