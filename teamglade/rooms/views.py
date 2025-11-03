from uuid import uuid4
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import ListView, DeleteView
from django.utils.decorators import method_decorator
from .models import Topic, Room, RoomUser, File
from .forms import NewTopicForm, SendInviteForm
import logging

# Set up logging for bot detection
logger = logging.getLogger(__name__)


@method_decorator(login_required, name='dispatch')
class RoomView(ListView):
    # model = Room
    context_object_name = 'topics'
    template_name = 'room.html'
    paginate_by = 12

    def get_context_data(self, **kwargs):
        my_user = self.request.user
        user_room = get_user_room(self.request)

        # list with id of all topics that was read by this user
        was_read = list(my_user.read_topics.all().values_list("id", flat=True))

        kwargs = {'room': user_room, 'was_read': was_read}

        return super().get_context_data(**kwargs)

    def get_queryset(self):
        user_room = get_user_room(self.request)

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

            for f in files:
                file = File.objects.create(
                    file=f,
                    topic=topic
                )

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

    def form_valid(self, form):
        my_user = self.request.user
        user_room = get_user_room(self.request)

        # if user is not owner/invited of this room - no permission to delete in another's room
        # prevent malicious deleting by user typing in the address bar
        if self.kwargs['pk'] not in user_room.topics.all().values_list("id", flat=True):
            raise Http404

        # if user is not owner of this room (invited user)
        if my_user.rooms.first() is None:
            # he can delete only own topics
            if self.kwargs['pk'] not in my_user.topics.all().values_list("id", flat=True):
                raise Http404

        return super(DeleteTopicView, self).form_valid(form)


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
        message = EmailMessage(subject, html_message, to=[email])  # FROM field will be DEFAULT_FROM_EMAIL
        message.send()

    def post(self, request, pk):
        # if user is not owner of this room (invited user)
        if self.request.user.rooms.first() is None:
            raise Http404

        form = SendInviteForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            invite_code = uuid4().hex[:8]  # generate random identifier - letters and digits
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

        if invited_user_obj is None:
            raise Http404

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

def message(request):
    """
    Accepts message form from home page and sends email with message
    """
    if request.method == 'POST':
        # Honeypot validation - if filled, it's a bot
        website = request.POST.get('website', '')
        email_confirmation = request.POST.get('email_confirmation', '')

        # If bot detected
        if website or email_confirmation:
            ip_address = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR', 'Unknown'))
            logger.warning(f"Home page honeypot triggered from IP {ip_address}. Bot send message attempt blocked. "
                           f"Website field: '{website}', "
                           f"Email confirmation field: '{email_confirmation}'")
            # and silently reject and redirect to home
            return redirect('home')

        name = request.POST['name']
        from_email = request.POST['email']
        phone = request.POST['phone']
        message = request.POST['message'] + "\n" + phone + "\n" + from_email

        subject = f"Site visitor's message. [{name}]"

        if is_email(from_email) and (len(name) < 31) and (len(message) < 191) and (len(phone) < 17):  # mini validation
            message = EmailMessage(subject, message, to=["lawagame@gmail.com"])  # FROM field will be DEFAULT_FROM_EMAIL
            message.send()
            return render(request, 'message_confirmation.html')

    return redirect('home')


def index(request):
    return render(request, 'index.html')


def policy(request):
    return render(request, 'privacy_policy.html')


def terms(request):
    return render(request, 'terms_conditions.html')


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


def is_email(email_string: str):
    from django.core.validators import validate_email
    from django.core.exceptions import ValidationError
    try:
        validate_email(email_string)
    except ValidationError:
        return False
    return True
