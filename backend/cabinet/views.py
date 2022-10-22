from django.contrib.auth.hashers import make_password
from rest_framework import generics, status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from cabinet.serializers import UserSerializer
from cabinet.tasks import send_update_mail
from users.models import User
from users.utils import RegisterUserMixin


class UserUpdateApiView(RegisterUserMixin, generics.RetrieveUpdateAPIView):
    """Редактирование профиля пользователя"""
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)
    lookup_field = 'username'

    def get_queryset(self):
        return User.objects.filter(is_active=True, is_verify=True,
                                   username=self.request.user.username)

    def update(self, request, *args, **kwargs):
        data = request.data
        user = request.user
        new_data = {
            'username': data.get(
                'username') if 'username' in data else user.username,
            'first_name': data.get(
                'first_name') if 'first_name' in data else user.first_name,
            'last_name': data.get(
                'last_name') if 'last_name' in data else user.last_name,
        }

        def update_token(request_user):
            """Обновление токена"""
            request_user.auth_token.delete()
            new_token = Token.objects.create(user=request_user)
            new_data['token'] = new_token

        if data.get('username'):
            update_token(user)
        if data.get('password'):
            new_data['password'] = make_password(data.get('password'))
            update_token(user)
        if data.get('email'):
            user = self.request.user
            if user.email != data.get('email'):
                self._get_serializer(data)
                key = self.generate_key(data.get('email'))
                user.activation_key = key
                user.save()
                send_update_mail.delay(data.get('email'), user.email, key)
        serializer = self._get_serializer(new_data)
        serializer.save()
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    def _get_serializer(self, data):
        serializer = self.serializer_class(instance=self.get_object(),
                                           data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        return serializer


class UpdateEmailApiView(generics.UpdateAPIView):
    """Изменение email"""
    permission_classes = (AllowAny,)
    lookup_field = ('email', 'new_email', 'activation_key',)

    def update(self, request, *args, **kwargs):
        user = User.objects.filter(activation_key=kwargs['activation_key'],
                                   email=kwargs['email']).first()
        if user:
            user.email = kwargs['new_email']
            user.activation_key = ''
            user.save()
            data = {'username': user.username, 'email': user.email}
            return Response(data=data, status=status.HTTP_200_OK)
        data = {'Update email': 'Invalid key'}
        return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
