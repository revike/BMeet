from django.urls import path

from cabinet.views import UserUpdateApiView, UpdateEmailApiView

app_name = 'cabinet'

urlpatterns = [
    path('<username>/', UserUpdateApiView.as_view(), name='profile'),
    path('<email>/<new_email>/<activation_key>/', UpdateEmailApiView.as_view(),
         name='mail_update'),
]
