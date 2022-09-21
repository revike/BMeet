from django.urls import path

from board.views import BoardListApiView

app_name = 'board'

urlpatterns = [
    path('', BoardListApiView.as_view(), name='boards'),
]
