from django.shortcuts import render
from django.http import HttpResponse
from .models import Room

def index(request):
    rooms = Room.objects.all()
    room_row = []

    for r in rooms:
        room_row.append(str(r.created_by) + '   ' + r.name)

    responce_html = '<br>'.join(room_row)

    return HttpResponse(responce_html)
