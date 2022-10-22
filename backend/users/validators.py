from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import re


def username_validate(value):
    """Валидация username"""
    regex = r"^[\w.@+-]+\Z"
    username_regex = re.search(regex, value)
    if len(value) < 2 or not username_regex:
        raise ValidationError(
            _('%(value)s is username must be more than 1 character and 150 '
              'characters or fewer. Letters, digits and @/./+/-/_ only.'),
            params={'value': value},
        )
