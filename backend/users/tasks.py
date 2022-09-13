from celery import shared_task
from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from django.urls import reverse

from users.models import User


@shared_task(autoretry_for=(Exception,),
             retry_kwargs={'max_retries': 7, 'countdown': 10})
def send_verify_mail(username, email, activation_key):
    url = settings.CORS_ALLOWED_ORIGINS[0]
    verify_url = reverse('users:verify', args=[email, activation_key])
    subject = 'Подтверждение учетной записи'
    message = f'{username}, для подтверждения учетной записи на сайте {url},' \
              f' перейдите по ссылке:\n{url}{verify_url}'
    return send_mail(subject, message, settings.EMAIL_HOST_USER,
                     [email], fail_silently=False)


@shared_task(autoretry_for=(Exception,),
             retry_kwargs={'max_retries': 10, 'countdown': 2})
def set_hash_password(username, email, password):
    user = User.objects.get(username=username, email=email, password=password)
    user.password = make_password(password)
    user.save()
