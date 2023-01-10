from rest_framework import serializers

from users.models import User
from users.serializers import RegisterModelSerializer


class UserSerializer(RegisterModelSerializer):
    """Сериализатор профиля пользователя"""
    token = serializers.SerializerMethodField('get_token')

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name', 'phone',
            'last_name', 'password', 'token'
        )

    @classmethod
    def get_token(cls, obj):
        return f'Token {obj.auth_token.key}'
