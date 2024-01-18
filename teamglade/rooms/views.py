from uuid import uuid4
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.core.mail import send_mail, EmailMessage
from django.template.loader import render_to_string
from django.urls import reverse
from django.views import View
from django.views.generic import ListView
from django.utils.decorators import method_decorator
from .models import Topic, Room, RoomUser
from .forms import NewTopicForm, NewTopicModelForm, SendInviteForm


@method_decorator(login_required, name='dispatch')
class RoomView(ListView):
    #model = Room
    context_object_name = 'topics'
    template_name = 'room.html'
    paginate_by = 12

    def get_context_data(self, **kwargs):
        my_user = self.request.user
        user_room = my_user.rooms.first()
        if user_room is None:
            user_room = my_user.member_of

        kwargs['room'] = user_room
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        my_user = self.request.user
        user_room = my_user.rooms.first()
        if user_room is None:
            user_room = my_user.member_of

        queryset = user_room.topics.all().order_by('-created_at')
        return queryset


@login_required
def room_FBV_version(request):
    my_user = request.user
    # room = get_object_or_404(Room, pk=pk)
    room = my_user.rooms.first()
    if room is None:
        room = my_user.member_of
    context = {'room': room}
    return render(request, 'room.html', context)


@login_required
def topic(request, pk):
    # TODO add topic viewed system
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


@method_decorator(login_required, name='dispatch')
class SendInviteView(View):
    def create_invited_user(self, request, invite_email, invite_code):
        user = RoomUser.objects.create_user(
            username=invite_email,
            email=invite_email,
            password=invite_code,
            invite_code=invite_code,
            member_of=request.user.rooms.first()
        )

    def send_invite_mail(self, request, email, invite_code):
        # generate link with identifier to login_invite view
        context = request.build_absolute_uri('/')[:-1] + reverse('login_invite', kwargs={'code': invite_code})
        html_message = render_to_string('invite_email.html', {'context': context, })
        subject = "[TeamGlade] You are invited to join TeamGlade room"
        from_email = "from@example.com"
        message = EmailMessage(subject, html_message, from_email, [email])
        message.send()

    def post(self, request, pk):
        form = SendInviteForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            invite_code = uuid4().hex[:8] # generate random identifier - letters and digits
            self.create_invited_user(request, email, invite_code)
            self.send_invite_mail(request, email, invite_code)
            return redirect('room')
        return render(request, 'send_invite.html', {'form': form})

    def get(self, request, pk):
        form = SendInviteForm()
        return render(request, 'send_invite.html', {'form': form})


class LoginInvitedView(View):
    def get(self, request, code):
        invited_user_obj = RoomUser.objects.filter(invite_code=code).first()
        invited_user = authenticate(username=invited_user_obj.username, password=invited_user_obj.invite_code)
        if invited_user is not None:
            login(request, invited_user)
        return redirect('room')


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
    # TODO add home page design
    return render(request, 'index.html')
