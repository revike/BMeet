from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail


@shared_task(autoretry_for=(Exception,),
             retry_kwargs={'max_retries': 7, 'countdown': 10})
def send_update_mail(email, email_old, key):
    """Отправка письма для обновления email"""
    url = settings.CORS_ALLOWED_ORIGINS[0]
    url_mail_update = f'/profile/{email_old}/{email}/{key}/'
    subject = 'Подтвердите изменение email'
    msg = f'Для изменения email перейдите по ссылке:\n{url}{url_mail_update}'
    return send_mail(subject, msg, settings.EMAIL_HOST_USER,
                     [email], fail_silently=False)
