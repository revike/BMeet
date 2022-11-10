from django.urls import path

from cabinet.views import UserUpdateDeleteApiView, UpdateEmailApiView

app_name = 'cabinet'

urlpatterns = [
    path('<username>/', UserUpdateDeleteApiView.as_view(), name='profile'),
    path('<email>/<new_email>/<activation_key>/', UpdateEmailApiView.as_view(),
         name='mail_update'),
]
