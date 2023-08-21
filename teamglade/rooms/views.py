from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.template import loader
#from django.urls import reverse

from .models import Topic, Room, RoomUser

def room(request):
    topics_list = Topic.objects.all()
    context = {'topics_list': topics_list, 'user_name': "My User Name", 'room_name': "My Room"}
    return render(request, 'room.html', context)

def new_topic(request, pk):
    pass

def index(request):
    return render(request, 'index.html')
