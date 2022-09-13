import hashlib
import random

from rest_framework import generics

from users.permissions import IsAnonymous
from users.serializers import RegisterModelSerializer
from users.tasks import send_verify_mail, set_hash_password


class RegisterApiView(generics.CreateAPIView):
    """Регистрация пользователя"""
    serializer_class = RegisterModelSerializer
    permission_classes = (IsAnonymous,)

    def perform_create(self, serializer):
        user = serializer.save()
        salt = hashlib.sha1(
            str(random.random()).encode('utf8')).hexdigest()[:6]
        user.activation_key = hashlib.sha1(
            (user.email + salt).encode('utf8')).hexdigest()
        user.save()
        send_verify_mail.delay(user.username, user.email, user.activation_key)
        set_hash_password.delay(user.username, user.email, user.password)


class VerificationKeyApiView(generics.UpdateAPIView):
    """Верификация пользователя"""
