from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.template import loader
#from django.urls import reverse

from .models import Topic, Room, RoomUser

def room(request):
    topics_list = Topic.objects.all()
    # user_name = RoomUser.objects.get(id=1)
    # print(user_name.username)
    context = {'topics_list': topics_list, 'user_name': "My User Name", 'room_name': "My Room"}
    #print(context)
    return render(request, 'room.html', context)

    # topics_list = Topic.objects.all().values()
    # template = loader.get_template('room.html')
    # context = {'topics_list' : topics_list}
    #
    # return HttpResponse(template.render(context, request))

def index(request):
    return render(request, 'index.html')
