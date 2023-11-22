from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('rooms/', views.room, name='room'),
    path('rooms/<int:pk>/new/', views.new_topic, name='new_topic'),
    path('rooms/<int:pk>/invite/', views.SendInviteView.as_view(), name='send_invite'),
    path('topic/<int:pk>/', views.topic, name='topic'),
]
