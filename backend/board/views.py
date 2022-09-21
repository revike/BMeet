from rest_framework import generics

from board.models import Board
from board.serializers import BoardSerializer, GroupSerializer
from users.models import User


class BoardListApiView(generics.ListCreateAPIView):
    serializer_class = BoardSerializer
    pagination_class = None

    def perform_create(self, serializer):
        author = self.request.user
        group = {author}
        group_data = self.request.data.get('group')
        if group_data:
            GroupSerializer(data=group_data, many=True).is_valid(
                raise_exception=True)
            for email in group_data:
                user = User.objects.filter(
                    email=email['email']).select_related().first()
                if user:
                    group.add(user.id)
                else:
                    print(
                        f'Отправить письмо с приглашением '
                        f'зарегистрироваться {email["email"]}')

        serializer.save(author=author, group=group)

    def get_queryset(self):
        return Board.objects.filter(is_active=True, group=self.request.user)
