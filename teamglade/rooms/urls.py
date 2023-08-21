from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),
    path('rooms/', views.room, name='room'),
    path('topic/<int:pk>/new/', views.new_topic, name='new_topic'),
]