from django.core.management import BaseCommand

from backend.settings import env
from users.models import User


class Command(BaseCommand):
    """Команда для создания супер юзера"""

    def handle(self, *args, **options):
        if not User.objects.filter(
                is_staff=True, is_superuser=True):

            User.objects.create_superuser(
                username=env('EMAIL_HOST_USER'), password='', is_active=False,
                email=env('EMAIL_HOST_USER'), is_verify=False)
