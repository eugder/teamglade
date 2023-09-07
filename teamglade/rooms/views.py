from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.template import loader
from .models import Topic, Room, RoomUser
from .forms import NewTopicForm, NewTopicModelForm

def room(request):
    topics_list = Topic.objects.all()
    context = {'topics_list': topics_list, 'user_name': "My User Name", 'room_name': "My Room"}
    return render(request, 'room.html', context)

def new_topic(request, pk):
    room = get_object_or_404(Room, pk=pk)

    if request.method == 'POST':
        form = NewTopicModelForm(request.POST)
        if form.is_valid():
            user = RoomUser.objects.first()

            topic = form.save(commit=False)
            topic.room = room
            topic.created_by = user
            topic.save()

            return redirect('room')
    else:
        form = NewTopicModelForm()

    return render(request, 'new_topic.html', {'form' : form})

def new_topic_from_class_version(request, pk):
    room = get_object_or_404(Room, pk=pk)

    if request.method == 'POST':
        form = NewTopicForm(request.POST)
        if form.is_valid():
            user = RoomUser.objects.first()

            topic = Topic.objects.create(
                room=room,
                title=form.cleaned_data['title'],
                message=form.cleaned_data['message'],
                created_by=user
            )
            return redirect('room')
    else:
        form = NewTopicForm()

    return render(request, 'new_topic.html', {'form' : form})

def new_topic_html_version(request, pk):
    room = get_object_or_404(Room, pk=pk)

    if request.method == 'POST':
        title = request.POST['title']
        message = request.POST['message']

        user = RoomUser.objects.first()

        topic = Topic.objects.create(
            room=room,
            title=title,
            message=message,
            created_by= user
        )

        return redirect('room')

    context = {'room' : room}
    return render(request, 'new_topic.html', context)

def index(request):
    return render(request, 'index.html')
