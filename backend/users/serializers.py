from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.authtoken.serializers import AuthTokenSerializer

from users.models import User


class RegisterModelSerializer(serializers.ModelSerializer):
    """Сериализатор регистрации"""

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')


class LoginSerializer(AuthTokenSerializer):
    """Сериализатор Login"""
    email = serializers.CharField(
        label=_("Email"),
        write_only=True
    )
    username = ...

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        if email and password:
            user = User.objects.filter(
                Q(username=email) | Q(email=email)).first()
            if not user or not user.check_password(password):
                msg = _('Unable to log in with provided credentials.')
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = _('Must include "username" and "password".')
            raise serializers.ValidationError(msg, code='authorization')
        attrs['user'] = user
        return attrs


class VerifyModelSerializer(serializers.ModelSerializer):
    """Сериализатор верификации"""

    class Meta:
        model = User
        fields = ('id', 'username', 'email')


class RecoverySerializer(serializers.ModelSerializer):
    """Сериализатор восстановления пароля"""

    class Meta:
        model = User
        fields = ('email',)
