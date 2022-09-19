from rest_framework import serializers

from users.models import User


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор профиля пользователя"""

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password',)
