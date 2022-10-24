from django.core.exceptions import ValidationError
import re


def username_validate(value):
    """Валидация username"""
    regex = r"^[a-zA-Z_-]+[a-zA-Z0-9_-]*"
    username_regex = re.search(regex, value)
    if len(value) < 2 or not username_regex:
        raise ValidationError(
            'Минимальная длина username 2 символа',
            params={'value': value})


def password_validate(value):
    """Валидация username"""
    regex = r"^[a-zA-Z_-]+[a-zA-Z0-9_-]*"
    username_regex = re.search(regex, value)
    if len(value) < 2 or not username_regex:
        raise ValidationError(
            'Минимальная длина username 2 символа',
            params={'value': value})
