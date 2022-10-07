from rest_framework import generics

from board.models import Board, NoRegisterUser
from board.serializers import BoardSerializer
from board.utils import AddUserBoardMixin


class BoardListApiView(AddUserBoardMixin, generics.ListCreateAPIView):
    """Список и создание досок"""
    serializer_class = BoardSerializer
    pagination_class = None

    def perform_create(self, serializer):
        email_list_register, email_list_no_register = self.save_serializer(
            self.request, serializer)
        self.sending_newsletter(serializer, email_list_register,
                                email_list_no_register)

    def get_queryset(self):
        return Board.objects.filter(is_active=True, group=self.request.user)


class BoardUpdateApiView(AddUserBoardMixin, generics.UpdateAPIView):
    """Редактирование досок"""
    serializer_class = BoardSerializer

    def get_queryset(self):
        return Board.objects.filter(is_active=True, author=self.request.user)

    def perform_update(self, serializer):
        board = self.get_object()
        no_register_users = NoRegisterUser.objects.filter(board=board)
        email_black_list_user = {i.email for i in board.group.all()}
        email_black_list_no_reg = {i.email for i in no_register_users}
        email_black_list = email_black_list_user ^ email_black_list_no_reg
        email_list_register, email_list_no_register = self.save_serializer(
            self.request, serializer)
        self.sending_newsletter(serializer, email_list_register,
                                email_list_no_register, email_black_list)


class BoardDeleteApiView(generics.DestroyAPIView):
    """Удаление досок"""

    def get_queryset(self):
        return Board.objects.filter(is_active=True, group=self.request.user)

    def perform_destroy(self, instance):
        user = self.request.user
        if user == instance.author:
            instance.is_active = False
        elif user in instance.group.all():
            instance.group.remove(user)
        instance.save()
