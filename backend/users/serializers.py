from django.core.validators import RegexValidator
from django.utils import timezone

from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.authtoken.serializers import AuthTokenSerializer

from users.models import User, TemporaryBanIp
from users.validators import validate_user_phone


class RegisterModelSerializer(serializers.ModelSerializer):
    """Сериализатор регистрации"""
    phone_number_regex = RegexValidator(regex=r"^[\+]|\d{10,12}$",
                                        message='number error')
    phone = serializers.CharField(max_length=12, required=False,
                                  validators=[phone_number_regex])

    class Meta:
        model = User
        fields = ('id', 'username', 'phone', 'email', 'password')

    @staticmethod
    def validate_email(value):
        norm_email = value.lower()
        if User.objects.filter(email=norm_email).exists():
            raise serializers.ValidationError("Not unique email")
        return norm_email

    @staticmethod
    def validate_phone(value):
        phone = validate_user_phone(value)
        return phone


class LoginSerializer(AuthTokenSerializer):
    """Сериализатор Login"""
    email = serializers.CharField(
        label=_("Email"),
        write_only=True
    )
    username = ...

    def validate(self, attrs):
        email = validate_user_phone(attrs.get('email'))
        password = attrs.get('password')

        if email and password:
            user = User.objects.filter(
                Q(username=email) | Q(email=email) | Q(phone=email)).first()
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
