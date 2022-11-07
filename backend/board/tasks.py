from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail


@shared_task(autoretry_for=(Exception,),
             retry_kwargs={'max_retries': 7, 'countdown': 10})
def send_mail_add_group(email, board_id):
    """Отправка письма приглашения в группу"""
    url = settings.CORS_ALLOWED_ORIGINS[0]
    url_board = f'/board/{board_id}/'
    subject = 'Приглашение группу!'
    msg = f'Вас пригласили в группу на сайте {url}.\n' \
          f'Доступно ссылке:\n{url}{url_board}'
    return send_mail(subject, msg, settings.EMAIL_HOST_USER,
                     [email], fail_silently=False)
