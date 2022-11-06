from django.utils import timezone

from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.authtoken.serializers import AuthTokenSerializer

from users.models import User, TemporaryBanIp


class RegisterModelSerializer(serializers.ModelSerializer):
    """Сериализатор регистрации"""

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password')

    def validate_email(self, value):
        norm_email = value.lower()
        if User.objects.filter(email=norm_email).exists():
            raise serializers.ValidationError("Not unique email")
        return norm_email


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


class TemporaryBanIpSerializer(serializers.ModelSerializer):
    """Сериализатор временной блокировки пользователя"""

    class Meta:
        model = TemporaryBanIp
        fields = ('ip_address', 'attempts', 'time_unblock', 'status')

    def get_or_create(self):
        instance, _ = TemporaryBanIp.objects.get_or_create(
            defaults={
                'ip_address': self.validated_data['ip_address'],
                'time_unblock': timezone.now()
            },
            ip_address=self.validated_data['ip_address']
        )
        return instance

    def delete_ip(self):
        TemporaryBanIp.objects.filter(
            ip_address=self.validated_data['ip_address']).delete()
