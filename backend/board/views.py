from rest_framework import generics

from board.models import Board
from board.serializers import BoardSerializer


class BoardListApiView(generics.ListCreateAPIView):
    serializer_class = BoardSerializer
    pagination_class = None

    def get_queryset(self):
        return Board.objects.filter(is_active=True, group=self.request.user)
