import hashlib
from random import random, randint

from board.models import NoRegisterUser, Board
from users.serializers import TemporaryBanIpSerializer
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
        no_register_user = NoRegisterUser.objects.filter(email=user.email)
        if no_register_user.count():
            for no_reg_user in no_register_user:
                board = Board.objects.get(id=no_reg_user.board.id)
                board.group.add(user)
                no_register_user.delete()
        token, create = Token.objects.get_or_create(user=user)
        if not create:
            user.auth_token.delete()
            token = Token.objects.create(user=user)
        return {
            'username': f'{token.user.username}',
            'token': f'Token {token.key}'
        }

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
        """Генератор пароля 8 символов, обязательно буквы верхнего и нижнего регистра, цифры, спецсимволы"""
        alphas = "abcdefghijklmnopqrstuvwxyz"
        alphas_cap = alphas.upper()
        numbers = "12345678901234567890123456"
        special_chars = "!_#$%^&*()_+/!#_$%^&*()_+/"
        password_characters = [alphas, alphas_cap, numbers, special_chars]
        new_password = ""
        for i in range(2):
            for j in range(4):
                chars_used = password_characters[j]
                char = chars_used[randint(0, 25)]
                new_password += char
        return new_password

    @staticmethod
    def delete_ip_from_temporary_ban(user_ip):
        update_ban_serializer = TemporaryBanIpSerializer(
            data={'ip_address': user_ip}
        )
        if update_ban_serializer.is_valid():
            update_ban_serializer.delete_ip()
