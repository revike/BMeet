from django.urls import path

from users.views import RegisterApiView, VerificationKeyApiView, \
    LogoutApiView, RecoveryPasswordApiView, \
    GeneratePasswordApiView, ResendApiView, LoginApiView, GoogleLoginApi, \
    VkLoginApiView

app_name = 'users'

urlpatterns = [
    path('login/', LoginApiView.as_view(), name='login'),
    path('register/', RegisterApiView.as_view(), name='register'),
    path('register/<int:pk>/', ResendApiView.as_view(), name='resend_email'),
    path('verify/<email>/<activation_key>/',
         VerificationKeyApiView.as_view(), name='verify'),
    path('logout/', LogoutApiView.as_view(), name='logout'),
    path('recovery/<email>/', RecoveryPasswordApiView.as_view(),
         name='send_recovery'),
    path('recovery/<email>/<activation_key>/',
         GeneratePasswordApiView.as_view(), name='recovery'),
    path('social/google/', GoogleLoginApi.as_view(), name='google'),
    path('social/vk/', VkLoginApiView.as_view(), name='vk'),
]
