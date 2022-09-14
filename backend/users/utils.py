import hashlib
import random
from users.tasks import send_verify_mail, set_hash_password


class RegisterUserMixin:
    """Mixin для создания пользователя и повторной отправки письма"""

    @staticmethod
    def register_user(serializer):
        user = serializer.save()
        salt = hashlib.sha1(
            str(random.random()).encode('utf8')).hexdigest()[:6]
        user.activation_key = hashlib.sha1(
            (user.email + salt).encode('utf8')).hexdigest()
        user.save()
        send_verify_mail.delay(user.username, user.email, user.activation_key)
        set_hash_password.delay(user.username, user.email, user.password)
