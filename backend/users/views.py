from django.db import IntegrityError
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.authtoken.models import Token

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
    queryset = User.objects.all()
    serializer_class = RegisterModelSerializer
    permission_classes = (IsAnonymous,)
    lookup_field = 'email'

    def update(self, request, *args, **kwargs):
        user = User.objects.filter(activation_key=kwargs['activation_key'],
                                   email=kwargs['email']).first()
        if user:
            user.is_verify = True
            user.activation_key = ''
            user.save()
            try:
                token = Token.objects.create(user=user)
            except IntegrityError:
                Token.objects.get(user=user).delete()
                token = Token.objects.create(user=user)
            data = {'token': f'Token {token.key}'}
            return Response(data=data, status=status.HTTP_200_OK)
        data = {'Activation key': 'Invalid key'}
        return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
