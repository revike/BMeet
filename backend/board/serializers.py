from rest_framework import serializers

from board.models import BoardData, Board
from users.models import User


class BoardDataSerializer(serializers.ModelSerializer):
    """Сериализатор данных доски"""

    class Meta:
        model = BoardData
        fields = '__all__'


class GroupSerializer(serializers.ModelSerializer):
    """Сериализатор группы пользователей"""
    email = serializers.EmailField(required=False)

    class Meta:
        model = User
        fields = ('email',)


class AuthorSerializer(serializers.ModelSerializer):
    """Сериализатор пользователя"""
    username = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)

    class Meta:
        model = User
        fields = ('id', 'username', 'email')


class BoardSerializer(serializers.ModelSerializer):
    """Сериализатор доски"""
    author = AuthorSerializer(required=False)
    group = GroupSerializer(many=True, required=False)

    class Meta:
        model = Board
        fields = '__all__'
