from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from cabinet.serializers import UserSerializer
from users.models import User


class UserUpdateApiView(generics.RetrieveUpdateAPIView):
    """Редактирование профиля пользователя"""
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)
    lookup_field = 'username'

    def get_queryset(self):
        return User.objects.filter(is_active=True, is_verify=True,
                                   username=self.request.user.username)

    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        if request.data.get('password') or request.data.get('email'):
            return Response(data=status.HTTP_400_BAD_REQUEST,
                            status=status.HTTP_400_BAD_REQUEST)
        return super().update(request, *args, **kwargs)
