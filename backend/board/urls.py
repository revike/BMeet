from django.urls import path

from board.views import BoardListApiView, BoardDeleteApiView

app_name = 'board'

urlpatterns = [
    path('', BoardListApiView.as_view(), name='boards'),
    path('delete/<int:pk>/', BoardDeleteApiView.as_view(), name='delete'),
]
