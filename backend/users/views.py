from django.contrib.auth.hashers import check_password
from django.db import IntegrityError
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView

from users.models import User
from users.permissions import IsAnonymous
from users.serializers import RegisterModelSerializer, UserSerializer
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
        data = serializer.validated_data
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        user = User.objects.filter(username=username, email=email,
                                   is_verify=False).first()
        if user and check_password(password, user.password):
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


class LogoutApiView(APIView):
    """Logout"""

    def get(self, request):
        request.user.auth_token.delete()
        return Response(data={'user': 'logout'}, status=status.HTTP_200_OK)


class UserApiView(generics.ListAPIView):
    """Пользователи для тестирования авторизации"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated,)