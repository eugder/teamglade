from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    #path('rooms/', views.room, name='room'),
    path('rooms/', views.RoomView.as_view(), name='room'),
    path('rooms/<int:pk>/new/', views.new_topic, name='new_topic'),
    path('rooms/<int:pk>/invite/', views.SendInviteView.as_view(), name='send_invite'),
    path('rooms/invite/<str:code>/', views.LoginInvitedView.as_view(), name='login_invite'),
    path('topic/<int:pk>/', views.topic, name='topic'),
    path('topic/<int:pk>/delete/', views.DeleteTopicView.as_view(), name='delete_topic'),
    path('message/', views.message, name='message'),
    path('policy/', views.policy, name='policy'),
]
