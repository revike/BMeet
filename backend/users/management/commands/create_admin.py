from django.core.management import BaseCommand

from users.models import User


class Command(BaseCommand):
    """Команда для создания супер юзера"""

    def handle(self, *args, **options):
        if not User.objects.filter(
                is_staff=True, is_superuser=True, is_active=True):
            User.objects.create_superuser(
                username='admin', password='admin', is_active=True,
                email='admin@admin.local', is_verify=True)
