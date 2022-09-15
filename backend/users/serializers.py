from rest_framework import serializers

from users.models import User


class RegisterModelSerializer(serializers.ModelSerializer):
    """Сериализатор регистрации"""

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')


class UserSerializer(serializers.ModelSerializer):
    """Временный Сериализатор для тестирования авторизации"""

    class Meta:
        model = User
        fields = '__all__'
