from rest_framework import generics

from users.models import User
from users.permissions import IsAnonymous
from users.serializers import RegisterModelSerializer
from users.utils import RegisterUserMixin


class RegisterApiView(RegisterUserMixin, generics.CreateAPIView,
                      generics.UpdateAPIView):
    """Регистрация пользователя и повторная отправка письма"""
    queryset = User.objects.all()
    serializer_class = RegisterModelSerializer
    permission_classes = (IsAnonymous,)

    def perform_create(self, serializer):
        self.register_user(serializer)

    def perform_update(self, serializer):
        self.register_user(serializer)


class VerificationKeyApiView(generics.UpdateAPIView):
    """Верификация пользователя"""
