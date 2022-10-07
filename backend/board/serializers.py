from rest_framework import serializers

from board.models import BoardData, Board, NoRegisterUser
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
    group_no_register = serializers.SerializerMethodField('get_no_register')

    class Meta:
        model = Board
        fields = '__all__'

    @classmethod
    def get_no_register(cls, board):
        """Получение незарегистрированных email"""
        return [{'email': i.email} for i in
                NoRegisterUser.objects.filter(board=board)]
