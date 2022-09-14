from django.urls import path
from rest_framework.authtoken.views import ObtainAuthToken

from users.views import RegisterApiView, VerificationKeyApiView

app_name = 'users'

urlpatterns = [
    path('login/', ObtainAuthToken.as_view(), name='login'),
    path('register/', RegisterApiView.as_view(), name='register'),
    path('register/<int:pk>/', RegisterApiView.as_view(), name='resend_email'),
    path('verify/<email>/<activation_key>/',
         VerificationKeyApiView.as_view(), name='verify'),
]
