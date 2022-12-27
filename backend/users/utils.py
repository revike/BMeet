import hashlib
import requests
from random import random
from rest_framework.exceptions import ValidationError
from board.models import NoRegisterUser, Board
from users.models import User
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
    def delete_ip_from_temporary_ban(user_ip):
        """Удаление блокировки ip"""
        update_ban_serializer = TemporaryBanIpSerializer(
            data={'ip_address': user_ip}
        )
        if update_ban_serializer.is_valid():
            update_ban_serializer.delete_ip()

    @staticmethod
    def get_user_social(url, params):
        """Запрос данных пользователя у Google"""
        response = requests.get(url, params=params)
        if not response.ok:
            raise ValidationError('Failed to obtain user info from Google.')
        return response.json()

    @staticmethod
    def create_user(email, data):
        """Создаем пользователя"""
        user = User.objects.filter(email=email).first()

        if not user:
            try:
                user = User.objects.create(**data)
            except (user.UniqueViolation, AttributeError):
                pass
        else:
            user.is_verify, user.is_active = True, True
            user.save()
            data['username'] = user.username
        return user, data

    @staticmethod
    def add_token(user, data):
        """Получаем токен"""
        token, created = Token.objects.get_or_create(user=user)
        data['token'] = f'Token {token.key}'
        return data
