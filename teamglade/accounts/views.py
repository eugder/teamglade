from django.contrib.auth import login, get_user_model, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from django.http import HttpResponseRedirect, Http404
from django.urls import reverse
from django.template.loader import render_to_string
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.views.generic import UpdateView
from rooms.models import RoomUser, Room
from .forms import RoomUserCreationForm, UserUpdateForm


@method_decorator(login_required, name='dispatch')
class UserUpdateView(UpdateView):
    template_name = 'my_account.html'
    form_class = UserUpdateForm

    def get_object(self):
        # let know UpdateView what exactly user is updating
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        user = self.request.user
        # if user is owner of this room he can edit room name, otherwise not
        if user.rooms.first() is not None:
            roomname_field = context['form'].fields["roomname"]
            roomname_field.initial = user.rooms.first().name
        else:
            roomname_field = context['form'].fields["roomname"]
            roomname_field.initial = user.member_of.name
            roomname_field.disabled = True
            roomname_field.help_text = "Invited users can't change room name"

        return context

    def form_valid(self, form):
        user = form.save()

        # if user is owner of this room - room name is saving, if invited user - not
        if user.rooms.first() is not None:
            room = user.rooms.first()
            room.name = form.cleaned_data['roomname']
            room.save()

        return HttpResponseRedirect(reverse('room'))

def signup(request):
    if request.method == 'POST':
        form = RoomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.is_active = False
            user.save()

            # all new users get a room
            new_room = Room.objects.create(
                name=str(user.username) + " room",
                created_by=user,)

            uidb64 = send_email_confirmation(request, user)

            # return render(request, 'email_confirmation_sent.html')
            return redirect('email_confirmation', uidb64=uidb64)
    else:
        form = RoomUserCreationForm()
    return render(request, 'signup.html', {'form': form})

def email_confirmation(request, uidb64):
    return render(request, 'email_confirmation_sent.html', {'context': uidb64})

def email_confirmed(request, uidb64, token):
    try:
        # catching errors caused by url with malicious broken uidb64 that leads to not existing user
        # or error with decode
        uid = urlsafe_base64_decode(uidb64)

        user_model = get_user_model()
        user = user_model.objects.get(pk=uid)
        if_valid = default_token_generator.check_token(user, token)

        if if_valid:
            user.is_active = True
            user.save()
            return render(request, 'email_confirmed.html')
    except:
        # in any other case as result is redirection to "email not confirmed"
        pass

    return render(request, 'email_not_confirmed.html', {'context': uidb64}) # here uidb64 for resend

def email_resend(request, uidb64):
    try:
        uid = urlsafe_base64_decode(uidb64)
        user_model = get_user_model()
        user = user_model.objects.get(pk=uid)
        send_email_confirmation(request, user)
    except:
        raise Http404

    return redirect('email_confirmation', uidb64=uidb64)

def send_email_confirmation(request, user):
    """
    Helper function. Sends email confirmation email with token to a user.

    Args:
        request (HttpRequest): link in email will be to URI that request came from.
        user (User): user to which send email.

    Returns:
        uidb64: uidb64 of user.
    """

    token = default_token_generator.make_token(user)
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))

    # generate link with user's id and its token
    context = request.build_absolute_uri('/')[:-1] + reverse('email_confirmed',
                                                             kwargs={'uidb64': uidb64, 'token': token})
    html_message = render_to_string('email_confirm_email_test.html', {'context': context, })
    subject = "[TeamGlade] Confirm your email address"
    message = EmailMessage(subject, html_message, to=[user.email])  # FROM field will be DEFAULT_FROM_EMAIL
    message.send()

    return uidb64
