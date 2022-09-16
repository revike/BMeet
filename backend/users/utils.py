import hashlib
from random import random

from django.db import IntegrityError

from users.tasks import send_verify_mail, set_hash_password
from rest_framework.authtoken.models import Token


class RegisterUserMixin:
    """Mixin для создания пользователя и повторной отправки письма"""

    def register_user(self, serializer):
        """Регистрация пользователя"""
        user = serializer.save()
        user.activation_key = self.generate_key(user.email)
        user.save()
        send_verify_mail.delay(user.username, user.email, user.activation_key)
        set_hash_password.delay(user.username, user.email, user.password)

    def resend_mail(self, user, password):
        """Повторная отправка ключа верификации"""
        user.activation_key = self.generate_key(user.email)
        user.save()
        send_verify_mail.delay(user.username, user.email, user.activation_key)
        set_hash_password.delay(user.username, user.email, password)

    @staticmethod
    def active_user(user):
        """Активация и верификация юзера"""
        user.is_verify, user.is_active = True, True
        user.activation_key = ''
        user.save()
        try:
            token = Token.objects.create(user=user)
        except IntegrityError:
            Token.objects.get(user=user).delete()
            token = Token.objects.create(user=user)
        return {'token': f'Token {token.key}'}

    @staticmethod
    def generate_key(email):
        """Генератор ключа"""
        salt = hashlib.sha1(
            str(random()).encode('utf8')).hexdigest()[:6]
        key = hashlib.sha1(
            (email + salt).encode('utf8')).hexdigest()
        return key

    @staticmethod
    def generate_password():
        """Генератор пароля"""
        return hashlib.sha1(str(random()).encode('utf8')).hexdigest()[:8]
