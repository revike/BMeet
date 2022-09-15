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

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        if username and password:
            user = User.objects.filter(
                Q(username=username) | Q(email=username)).filter(
                is_verify=True).first()
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


class UserSerializer(serializers.ModelSerializer):
    """Временный Сериализатор для тестирования авторизации"""

    class Meta:
        model = User
        fields = '__all__'
