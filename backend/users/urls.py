from django.urls import path
from rest_framework.authtoken.views import ObtainAuthToken

from users.views import RegisterApiView, VerificationKeyApiView, LogoutApiView, \
    UserApiView

app_name = 'users'

urlpatterns = [
    path('login/', ObtainAuthToken.as_view(), name='login'),
    path('register/', RegisterApiView.as_view(), name='register'),
    path('register/<int:pk>/', RegisterApiView.as_view(), name='resend_email'),
    path('verify/<email>/<activation_key>/',
         VerificationKeyApiView.as_view(), name='verify'),
    path('logout/', LogoutApiView.as_view(), name='logout'),
    path('users/', UserApiView.as_view(), name='users'),
]
