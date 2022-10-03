from rest_framework import serializers

from users.models import User


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор профиля пользователя"""
    token = serializers.SerializerMethodField('get_token')

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name',
            'last_name', 'password', 'token'
        )

    @classmethod
    def get_token(cls, obj):
        return f'Token {obj.auth_token.key}'
