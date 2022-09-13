from django.urls import path
from rest_framework.authtoken.views import ObtainAuthToken

from users.views import RegisterApiView

app_name = 'users'

urlpatterns = [
    path('token/', ObtainAuthToken.as_view(), name='token'),
    path('register/', RegisterApiView.as_view(), name='register'),
]
