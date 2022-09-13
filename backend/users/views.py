from rest_framework import generics, permissions, status
from rest_framework.authtoken.models import Token
from rest_framework.response import Response

from users.serializers import RegisterModelSerializer


class RegisterApiView(generics.CreateAPIView):
    """Регистрация пользователя"""
    serializer_class = RegisterModelSerializer
    permission_classes = (permissions.AllowAny,)

    def perform_create(self, serializer):
        super().perform_create(serializer)
        if serializer.data:
            print('send_mail')

    def create(self, request, *args, **kwargs):
        try:
            token = self.request.headers['Authorization']
            if Token.objects.filter(key=token.split()[1]).first():
                return Response(data={'detail': 'You are already logged in'},
                                status=status.HTTP_400_BAD_REQUEST)
        except KeyError:
            return super().create(request, *args, **kwargs)
