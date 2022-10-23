from django.core.exceptions import ValidationError

from cabinet.utils import username_check


def username_validate(value):
    """Валидация username"""
    if not username_check(value):
        raise ValidationError(
            'Username должен начинаться с буквы и может содержать знаки - или _ (минимальная длина 2 символа)',
            params={'value': value})
