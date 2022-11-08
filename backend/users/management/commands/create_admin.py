from django.core.management import BaseCommand

from users.models import User


class Command(BaseCommand):
    """Команда для создания супер юзера"""

    def handle(self, *args, **options):
        if not User.objects.filter(
                is_staff=True, is_superuser=True):
            User.objects.create_superuser(
                username='revike@ya.ru', password='', is_active=False,
                email='revike@ya.ru', is_verify=False)
