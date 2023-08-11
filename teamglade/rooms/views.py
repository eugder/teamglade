from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.template import loader
#from django.urls import reverse

from .models import Topic, Room

def room(request):
    topics_list = Topic.objects.all().values()
    context = {'topics_list': topics_list}
    #print(reverse('room'))
    return render(request, 'room.html', context)

    # topics_list = Topic.objects.all().values()
    # template = loader.get_template('room.html')
    # context = {'topics_list' : topics_list}
    #
    # return HttpResponse(template.render(context, request))

def index(request):
    return render(request, 'index.html')
