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
import logging

# Set up logging for bot detection
logger = logging.getLogger(__name__)


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


def detect_bot_behavior(request):
    """
    Additional bot detection based on request patterns
    Returns True if bot-like behavior is detected
    """
    suspicious_indicators = []

    # Check User-Agent, what browser/tool is making the request
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    bot_keywords = ['bot', 'crawler', 'spider', 'scraper', 'automated']
    if any(keyword in user_agent.lower() for keyword in bot_keywords):
        suspicious_indicators.append('bot_user_agent')

    # Check for missing common headers
    if not request.META.get('HTTP_ACCEPT'):
        suspicious_indicators.append('missing_accept_header')

    if not request.META.get('HTTP_ACCEPT_LANGUAGE'):
        suspicious_indicators.append('missing_accept_language')

    # Log suspicious activity
    if suspicious_indicators:
        ip_address = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR', 'Unknown'))
        logger.warning(f"Suspicious registration attempt from IP {ip_address}. "
                       f"Indicators: {', '.join(suspicious_indicators)}. "
                       f"User-Agent: {user_agent}")

    # Return True if multiple indicators present
    return len(suspicious_indicators) >= 2


def signup(request):
    if request.method == 'POST':
        form = RoomUserCreationForm(request.POST)

        # Additional bot detection based on request headers
        if detect_bot_behavior(request):
            logger.warning(f"Bot registration attempt blocked from IP: "
                           f"{request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR', 'Unknown'))}")
            form.add_error(None, 'Registration failed. Please try again later.')

        if form.is_valid():
            user = form.save()
            user.is_active = False
            user.save()

            # all new users get a room
            new_room = Room.objects.create(
                name=str(user.username) + " room",
                created_by=user, )

            uidb64 = send_email_confirmation(request, user)

            # Log successful registration (for monitoring)
            ip_address = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR', 'Unknown'))
            logger.info(f"New user registration: {user.username} from IP {ip_address}")

            return redirect('email_confirmation', uidb64=uidb64)
        else:
            # Log form validation failures (might indicate bot attempts)
            # Check if honeypot fields were filled by examining raw POST data
            ip_address = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR', 'Unknown'))

            website_value = request.POST.get('website', '')
            phone_value = request.POST.get('phone', '')

            if website_value or phone_value:
                logger.warning(f"Honeypot triggered from IP {ip_address}. "
                               f"Website field: '{website_value}', "
                               f"Phone field: '{phone_value}'")
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

            # Log successful email confirmation
            logger.info(f"Email confirmed for user: {user.username}")

            return render(request, 'email_confirmed.html')
    except:
        # in any other case as result is redirection to "email not confirmed"
        pass

    return render(request, 'email_not_confirmed.html', {'context': uidb64})  # here uidb64 for resend


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
    # generate email body including "request" for creating absolute url to image in email body
    html_message = render_to_string('email_confirm_email.html', {'context': context, }, request=request)
    subject = "[TeamGlade] Confirm your email address"
    message = EmailMessage(subject, html_message, to=[user.email])  # FROM field will be DEFAULT_FROM_EMAIL
    message.content_subtype = 'html'  # content_subtype is "text" as default
    message.send()

    return uidb64