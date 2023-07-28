from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader

from .models import Topic, Room

def room(request):
    topics_list = Topic.objects.all().values()
    template = loader.get_template('room.html')
    context = {'topics_list' : topics_list}

    return HttpResponse(template.render(context, request))

def index(request):
    rooms = Room.objects.all()
    room_row = []

    for r in rooms:
        room_row.append(str(r.created_by) + '   ' + r.name)

    responce_html = '<br>'.join(room_row)

    return HttpResponse(responce_html)
