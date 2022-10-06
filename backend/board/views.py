from rest_framework import generics

from board.models import Board, NoRegisterUser
from board.serializers import BoardSerializer, GroupSerializer
from board.tasks import send_mail_add_group
from users.models import User


class BoardListApiView(generics.ListCreateAPIView):
    """Список и создание досок"""
    serializer_class = BoardSerializer
    pagination_class = None

    def perform_create(self, serializer):
        author = self.request.user
        email_list_no_register = set()
        email_list_register = set()
        group = {author}
        group_data = self.request.data.get('group')
        if group_data:
            GroupSerializer(data=group_data, many=True).is_valid(
                raise_exception=True)
            for email in group_data:
                user = User.objects.filter(
                    email=email['email']).select_related().first()
                if user:
                    if self.request.user.email == email['email']:
                        continue
                    group.add(user.id)
                    email_list_register.add(email['email'])
                else:
                    email_list_no_register.add(email['email'])

        serializer.save(author=author, group=group)

        board_id = serializer.data.get('id')
        if email_list_register:
            for email in email_list_register:
                send_mail_add_group.delay(email, board_id)
        if email_list_no_register:
            board = Board.objects.get(id=board_id)
            for email in email_list_no_register:
                send_mail_add_group.delay(email, board_id)
                NoRegisterUser.objects.create(board=board, email=email)

    def get_queryset(self):
        return Board.objects.filter(is_active=True, group=self.request.user)


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