from celery import shared_task
from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail

from users.models import User


@shared_task(autoretry_for=(Exception,),
             retry_kwargs={'max_retries': 7, 'countdown': 10})
def send_verify_mail(username, email, activation_key):
    """Отправка email с key verification"""
    url = settings.CORS_ALLOWED_ORIGINS[0]
    verify_url = f'/users/verify/{email}/{activation_key}/'
    subject = 'Подтверждение учетной записи'
    message = f'{username}, для подтверждения учетной записи на сайте {url},' \
              f' перейдите по ссылке:\n{url}{verify_url}'
    return send_mail(subject, message, settings.EMAIL_HOST_USER,
                     [email], fail_silently=False)


@shared_task(autoretry_for=(Exception,),
             retry_kwargs={'max_retries': 10, 'countdown': 2})
def set_hash_password(username, email, password):
    """Hashing пароля и сохранение в базу"""
    user = User.objects.get(username=username, email=email, password=password)
    user.password = make_password(password)
    user.save()


@shared_task(autoretry_for=(Exception,),
             retry_kwargs={'max_retries': 7, 'countdown': 10})
def send_recovery_mail(email, key):
    """Отправка email для подтверждения восстановления пароля"""
    url = settings.CORS_ALLOWED_ORIGINS[0]
    recovery_url = f'/users/recovery/{email}/{key}/'
    subject = 'Восстановление пароля'
    message = f'Если вы хотите восстановить пароль, ' \
              f'перейдите по ссылке:\n{url}{recovery_url}\n'
    return send_mail(subject, message, settings.EMAIL_HOST_USER,
                     [email], fail_silently=False)


@shared_task(autoretry_for=(Exception,),
             retry_kwargs={'max_retries': 7, 'countdown': 10})
def send_new_password(username, email, password):
    """Отправка email с новым паролем"""
    subject = 'Новый пароль'
    message = f'Вы восстановили пароль.\nВ целях безопасности просим ' \
              f'его изменить в личном кабинете.\n' \
              f'Username: {username}\nEmail: {email}\nПароль: {password}'
    return send_mail(subject, message, settings.EMAIL_HOST_USER,
                     [email], fail_silently=False)
