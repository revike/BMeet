from django.contrib.auth.hashers import check_password, make_password
from rest_framework import generics, status
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import User
from users.permissions import IsAnonymous
from users.serializers import RegisterModelSerializer, \
    RecoverySerializer, VerifyModelSerializer, LoginSerializer
from users.tasks import send_recovery_mail, send_new_password
from users.utils import RegisterUserMixin


class RegisterApiView(RegisterUserMixin, generics.CreateAPIView):
    """Регистрация пользователя и повторная отправка письма"""
    queryset = User.objects.all()
    serializer_class = RegisterModelSerializer
    permission_classes = (IsAnonymous,)

    def perform_create(self, serializer):
        self.register_user(serializer)


class ResendApiView(RegisterUserMixin, generics.UpdateAPIView):
    """Повторная отправка письма для верификации"""
    serializer_class = RegisterModelSerializer
    permission_classes = (IsAnonymous,)

    def update(self, request, *args, **kwargs):
        data = self.request.data
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        user = User.objects.filter(id=kwargs['pk'], username=username,
                                   email=email, is_verify=False).first()
        if user and check_password(password, user.password):
            self.resend_mail(user, password)
            return Response(data=self.request.data, status=status.HTTP_200_OK)
        data = {'Invalid': 'The request failed'}
        return Response(data=data, status=status.HTTP_400_BAD_REQUEST)


class VerificationKeyApiView(RegisterUserMixin, generics.UpdateAPIView):
    """Верификация пользователя"""
    queryset = User.objects.all()
    serializer_class = VerifyModelSerializer
    permission_classes = (IsAnonymous,)
    lookup_field = ('email', 'activation_key',)

    def update(self, request, *args, **kwargs):
        user = User.objects.filter(activation_key=kwargs['activation_key'],
                                   email=kwargs['email']).first()
        if user:
            data = self.active_user(user)
            return Response(data=data, status=status.HTTP_200_OK)
        data = {'Activation key': 'Invalid key'}
        return Response(data=data, status=status.HTTP_400_BAD_REQUEST)


class LoginApiView(ObtainAuthToken):
    """Login"""
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        data = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'is_verify': user.is_verify
        }
        if not user.is_verify:
            return Response(data=data, status=status.HTTP_403_FORBIDDEN)
        token, created = Token.objects.get_or_create(user=user)
        data['token'] = f'Token {token.key}'
        return Response(data=data, status=status.HTTP_200_OK)


class LogoutApiView(APIView):
    """Logout"""

    def get(self, request):
        request.user.auth_token.delete()
        return Response(data={'user': 'logout'}, status=status.HTTP_200_OK)


class RecoveryPasswordApiView(RegisterUserMixin, generics.UpdateAPIView):
    """Восстановление пароля"""
    serializer_class = RecoverySerializer
    permission_classes = (IsAnonymous,)
    lookup_field = 'email'

    def update(self, request, *args, **kwargs):
        email = kwargs['email']
        user = User.objects.filter(email=email).first()
        if user:
            key = self.generate_key(email)
            user.activation_key = key
            user.save()
            send_recovery_mail.delay(email, key)
            return Response(data={'email': email}, status=status.HTTP_200_OK)
        return Response(data={'Invalid': 'Email does not exist'},
                        status=status.HTTP_400_BAD_REQUEST)


class GeneratePasswordApiView(RegisterUserMixin, generics.UpdateAPIView):
    """Генерация нового пароля"""
    serializer_class = RecoverySerializer
    permission_classes = (IsAnonymous,)
    lookup_field = ('email', 'key',)

    def update(self, request, *args, **kwargs):
        user = User.objects.filter(activation_key=kwargs['activation_key'],
                                   email=kwargs['email']).first()
        if user:
            password = self.generate_password()
            user.password = make_password(password)
            user.save()
            data = self.active_user(user)
            send_new_password.delay(user.username, user.email, password)
            return Response(data=data, status=status.HTTP_200_OK)
        data = {'Activation key': 'Invalid key'}
        return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
