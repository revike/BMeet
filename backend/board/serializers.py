from datetime import datetime

from rest_framework import serializers

from board.models import BoardData, Board, NoRegisterUser, BoardMessage
from users.models import User


class GroupSerializer(serializers.ModelSerializer):
    """Сериализатор группы пользователей"""
    email = serializers.EmailField(required=False)
    username = serializers.CharField(required=False)

    class Meta:
        model = User
        fields = ('username', 'email',)


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
    group_no_register = serializers.SerializerMethodField()
    is_active = serializers.BooleanField(required=False, default=True)

    class Meta:
        model = Board
        fields = ('id', 'name', 'description', 'is_active', 'created',
                  'updated', 'author', 'group', 'group_no_register',)

    @classmethod
    def get_group_no_register(cls, board):
        """Получение незарегистрированных email"""
        no_register_users = NoRegisterUser.objects.filter(board=board)
        return [{'email': i.email} for i in no_register_users]


class BoardDataSerializer(serializers.ModelSerializer):
    """Сериализатор данных доски"""
    author = AuthorSerializer(required=False)
    group = GroupSerializer(many=True, required=False)
    group_no_register = serializers.SerializerMethodField()
    chat = serializers.SerializerMethodField()
    data_board = serializers.SerializerMethodField()

    class Meta:
        model = Board
        fields = (
            'name', 'description', 'is_active', 'created', 'updated', 'author',
            'group', 'group_no_register', 'chat', 'data_board')

    @classmethod
    def get_group_no_register(cls, board):
        """Получение незарегистрированных email"""
        no_register_users = NoRegisterUser.objects.filter(board=board)
        return [{'email': i.email} for i in no_register_users]

    @classmethod
    def get_chat(cls, board):
        chat = BoardMessage.objects.filter(board=board)
        return [
            {
                'user_id': i.user_id.id,
                'username': i.user_id.username,
                'message': i.message,
                'datetime': datetime.strftime(i.datetime, '%Y-%m-%d %H:%M:%S')
            } for i in chat
        ]

    @classmethod
    def get_data_board(cls, board):
        data_board = BoardData.objects.filter(board=board)
        return [
            {
                'data': i.data
            } for i in data_board
        ]
