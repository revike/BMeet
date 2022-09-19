from django.urls import path

from cabinet.views import UserUpdateApiView

app_name = 'cabinet'

urlpatterns = [
    path('<username>/', UserUpdateApiView.as_view(), name='profile'),
]
