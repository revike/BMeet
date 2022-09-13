import hashlib
import random

from django.contrib.auth.hashers import make_password
from rest_framework import serializers

from users.models import User


class RegisterModelSerializer(serializers.ModelSerializer):
    """Сериализатор регистрации"""

    class Meta:
        model = User
        fields = ('username', 'email', 'password')

    def save(self, **kwargs):
        user = super().save()
        salt = hashlib.sha1(
            str(random.random()).encode('utf8')).hexdigest()[:6]
        user.activation_key = hashlib.sha1(
            (user.email + salt).encode('utf8')).hexdigest()
        user.password = make_password(user.password)
        user.save()
        return user
