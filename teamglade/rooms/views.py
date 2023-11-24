from uuid import uuid4
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.core.mail import send_mail, EmailMessage
from django.template.loader import render_to_string
from django.urls import reverse
from django.views import View
from .models import Topic, Room, RoomUser
from .forms import NewTopicForm, NewTopicModelForm, SendInviteForm


@login_required
def room(request):
    my_user = request.user
    # room = get_object_or_404(Room, pk=pk)
    room = my_user.rooms.first()
    context = {'room': room}
    return render(request, 'room.html', context)


@login_required
def topic(request, pk):
    the_topic = get_object_or_404(Topic, pk=pk)
    context = {'topic': the_topic}
    return render(request, 'topic.html', context)


@login_required
def new_topic(request, pk):
    room_obj = get_object_or_404(Room, pk=pk)

    # if user is not owner of this room (no permission to create new topic here)
    if request.user.rooms.first().pk != pk:
        raise Http404

    if request.method == 'POST':
        form = NewTopicForm(request.POST)
        if form.is_valid():
            user = request.user

            topic = Topic.objects.create(
                room=room_obj,
                title=form.cleaned_data['title'],
                message=form.cleaned_data['message'],
                created_by=user
            )
            return redirect('room')
    else:
        form = NewTopicForm()

    return render(request, 'new_topic.html', {'form': form})


class SendInviteView(View):
    def send_invite_mail(self, request):
        invite_code = uuid4().hex[:8]
        context = request.build_absolute_uri('/')[:-1] + reverse('login_invite', kwargs={'code': invite_code})
        html_message = render_to_string('invite_email.html', {'context': context, })
        message = EmailMessage("subject", html_message, "from@example.com", ["to@example.com"])
        #message.content_subtype = 'html'  # this is required because there is no plain text email message
        message.send()

        # send_mail(
        #     "Subject here",
        #     "Here is the message.",
        #     "from@example.com",
        #     ["to@example.com"],
        #     fail_silently=False,
        # )

    def post(self, request, pk):
        form = SendInviteForm(request.POST)
        if form.is_valid():
            self.send_invite_mail(request)
            return redirect('room')
        return render(request, 'send_invite.html', {'form': form})

    def get(self, request, pk):
        form = SendInviteForm()
        return render(request, 'send_invite.html', {'form': form})

class LoginInviteView(View):
    pass

def new_topic_ModelForm_version(request, pk):
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

    return render(request, 'new_topic.html', {'form': form})


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
            created_by=user
        )

        return redirect('room')

    context = {'room': room}
    return render(request, 'new_topic.html', context)


def index(request):
    return render(request, 'index.html')
