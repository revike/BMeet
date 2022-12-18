import re

from django.core.exceptions import ValidationError

from cabinet.utils import username_check, password_check


def username_validate(value):
    """Валидация username"""
    if not username_check(value):
        raise ValidationError(
            'Username должен начинаться с буквы и может содержать'
            ' знаки - или _ (минимальная длина 2 символа)',
            params={'value': value})


def password_validate(value):
    """Валидация password"""
    if not password_check(value):
        raise ValidationError(
            'Пароль не удовлетворяет условиям безопасности',
            params={'value': value})


def validate_user_phone(value):
    """Валидация phone"""
    pattern = r'^[\+]|\d{10,12}$'
    if re.search(pattern, value):
        if value[:1] == '8' or value[:2] == '+7' or len(value) == 10:
            code = '+7'
            value = f'{code}{value[-10:]}'
    return value
