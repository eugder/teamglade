from uuid import uuid4
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.core.mail import send_mail, EmailMessage
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import ListView, DeleteView
from django.utils.decorators import method_decorator
from .models import Topic, Room, RoomUser, File
from .forms import NewTopicForm, NewTopicModelForm, SendInviteForm


@method_decorator(login_required, name='dispatch')
class RoomView(ListView):
    #model = Room
    context_object_name = 'topics'
    template_name = 'room.html'
    paginate_by = 12

    def get_context_data(self, **kwargs):
        my_user = self.request.user
        user_room = get_user_room(self.request)
        # user_room = my_user.rooms.first()
        # if user_room is None:
        #     user_room = my_user.member_of

        # list with id of all topics that was read by this user
        was_read = list(my_user.read_topics.all().values_list("id", flat=True))

        kwargs = {'room': user_room, 'was_read': was_read}

        return super().get_context_data(**kwargs)

    def get_queryset(self):
        user_room = get_user_room(self.request)
        # my_user = self.request.user
        # user_room = my_user.rooms.first()
        # if user_room is None:
        #     user_room = my_user.member_of

        queryset = user_room.topics.all().order_by('-created_at')
        return queryset


# @login_required
# def room_FBV_version(request):
#     my_user = request.user
#     # room = get_object_or_404(Room, pk=pk)
#     room = my_user.rooms.first()
#     if room is None:
#         room = my_user.member_of
#     context = {'room': room}
#     return render(request, 'room.html', context)


@login_required
def topic(request, pk):
    user_room = get_user_room(request)

    the_topic = get_object_or_404(Topic, pk=pk)

    # if user is not owner/member of this room (no permission to read topic)
    if the_topic not in user_room.topics.all():
        raise Http404

    # topic marked as was read by this user
    the_topic.was_read_by.add(request.user)

    context = {'topic': the_topic}
    return render(request, 'topic.html', context)


@login_required
def new_topic(request, pk):
    room_obj = get_object_or_404(Room, pk=pk)

    # if user is not owner/invited of this room (no permission to create new topic here)
    user_room = get_user_room(request)
    # if request.user.rooms.first().pk != pk:
    if user_room.pk != pk:
        raise Http404

    if request.method == 'POST':
        form = NewTopicForm(request.POST, request.FILES)
        if form.is_valid():
            user = request.user

            topic = Topic.objects.create(
                room=room_obj,
                title=form.cleaned_data['title'],
                message=form.cleaned_data['message'],
                # files=request.FILES['files'],
                created_by=user,
            )

            # adding files
            files = request.FILES.getlist('files')
            # print(type(request.FILES))
            for f in files:
                file = File.objects.create(
                    file=f,
                    topic=topic
                )
                # print(f)

            # new topic marked as was read by creator
            topic.was_read_by.add(user)

            return redirect('room')
    else:
        form = NewTopicForm()

    return render(request, 'new_topic.html', {'form': form})


@method_decorator(login_required, name='dispatch')
class DeleteTopicView(DeleteView):
    model = Topic
    context_object_name = 'topic'
    success_url = reverse_lazy('room')
    template_name = "topic_confirm_delete.html"

    # def form_valid(self, form):
    #     my_user = super.request.user
    #     # if user is not owner of this room (invited user)
    #     if my_user.rooms.first() is None:
    #         # he can delete only own topics
    #         if self.pk not in my_user.topics.all().values_list("id", flat=True) :
    #             raise Http404
    #     return super(DeleteTopicView, self).form_valid(form)

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


# def new_topic_ModelForm_version(request, pk):
#     room = get_object_or_404(Room, pk=pk)
#
#     if request.method == 'POST':
#         form = NewTopicModelForm(request.POST)
#         if form.is_valid():
#             user = RoomUser.objects.first()
#
#             topic = form.save(commit=False)
#             topic.room = room
#             topic.created_by = user
#             topic.save()
#
#             return redirect('room')
#     else:
#         form = NewTopicModelForm()
#
#     return render(request, 'new_topic.html', {'form': form})


# def new_topic_html_version(request, pk):
#     room = get_object_or_404(Room, pk=pk)
#
#     if request.method == 'POST':
#         title = request.POST['title']
#         message = request.POST['message']
#
#         user = RoomUser.objects.first()
#
#         topic = Topic.objects.create(
#             room=room,
#             title=title,
#             message=message,
#             created_by=user
#         )
#
#         return redirect('room')
#
#     context = {'room': room}
#     return render(request, 'new_topic.html', context)


def index(request):
    return render(request, 'index.html')


def get_user_room(request):
    """
    Helper function.
    User has to have room in which he can operate.
    If user is owner - there is a room with relation to user (Room.created_by).
    If user is invited member - he has a relation to Room (field member_of).
    Function returns Room object in which user can operate.
    """
    my_user = request.user
    user_room = my_user.rooms.first()
    if user_room is None:
        user_room = my_user.member_of
        if user_room is None:
            # not standard case
            raise Http404
    return (user_room)
