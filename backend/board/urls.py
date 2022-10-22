from django.urls import path

from board.views import BoardListApiView, BoardDeleteApiView, \
    BoardUpdateApiView, BoardDetailApiView

app_name = 'board'

urlpatterns = [
    path('', BoardListApiView.as_view(), name='boards'),
    path('<int:pk>/', BoardDetailApiView.as_view(), name='board_detail'),
    path('delete/<int:pk>/', BoardDeleteApiView.as_view(), name='delete'),
    path('update/<int:pk>/', BoardUpdateApiView.as_view(), name='update'),
]
