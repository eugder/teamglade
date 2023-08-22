from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, Http404
from django.template import loader
#from django.urls import reverse

from .models import Topic, Room, RoomUser

def room(request):
    topics_list = Topic.objects.all()
    context = {'topics_list': topics_list, 'user_name': "My User Name", 'room_name': "My Room"}
    return render(request, 'room.html', context)

def new_topic(request, pk):
    room = get_object_or_404(Room, pk=pk)
    context = {'room' : room}
    return render(request, 'new_topic.html', context)

def index(request):
    return render(request, 'index.html')
