#from django.contrib.auth.forms import UserCreationForm
from django.core import mail
from django.urls import reverse, resolve
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.test import TestCase
from ..views import signup
#from ..rooms.models import RoomUser
from rooms.models import RoomUser
from ..views import RoomUserCreationForm

class SignUpTests(TestCase):
    def setUp(self):
        # Sending request to SignUp page
        self.url = reverse('signup')
        self.response = self.client.get(self.url)

    def test_sighnup_status_code(self):
        self.assertEquals(self.response.status_code, 200)

    def test_signup_url_resolves_signup_view(self):
        # URL named 'signup' leads to correct func
        view = resolve(self.url)
        self.assertEquals(view.func, signup)

    def test_csrf(self):
        # Response contains a token
        self.assertContains(self.response, 'csrfmiddlewaretoken')

    def test_contains_form(self):
        # Response contains a correct form
        form = self.response.context.get('form')
        self.assertIsInstance(form, RoomUserCreationForm)

    def test_form_inputs(self):
        # The view must contain five inputs:
        # csrf, username, email, password1, password2
        self.assertContains(self.response, '<input', 5)
        self.assertContains(self.response, 'type="text"', 1)
        self.assertContains(self.response, 'type="email"', 1)
        self.assertContains(self.response, 'type="password"', 2)

class SuccessfulSignUpTests(TestCase):
    def setUp(self):
        url = reverse('signup')
        data = {
            'username': 'john',
            'email': 'john@doe.com',
            'password1': 'abcdef123456',
            'password2': 'abcdef123456'
        }
        # Create a new user
        self.response = self.client.post(url, data)
        self.home_url = reverse('home')
        uid = RoomUser.objects.all().first().id
        self.uidb64 = urlsafe_base64_encode(force_bytes(uid))
        self.email_confirmation_url = reverse('email_confirmation', kwargs={'uidb64': self.uidb64})
        self.email = mail.outbox[0]

    def test_redirection(self):
        # A valid form submission should redirect the user to the email_confirmation page
        # (302 code, 200 code means not correct filled data in form in setUp)
        self.assertRedirects(self.response, self.email_confirmation_url)

    def test_user_creation(self):
        # User was created
        self.assertTrue(RoomUser.objects.exists())

    def test_user_no_authentication(self):
        # Create a new request to a home page. The resulting response should now have a `user` to its context.
        # and this user should be AnonymousUser (not logged in as far as user is not active yet)
        response = self.client.get(self.home_url)
        user = response.context.get('user')
        self.assertTrue(user.is_anonymous)

    def test_email_confirmation_subject(self):
        self.assertEqual('[TeamGlade] Confirm your email address', self.email.subject)

    def test_email_confirmation_to(self):
        self.assertEqual(['john@doe.com',], self.email.to)

    def test_email_confirmation_body_uidb64(self):
        # email body has a link to email_confirmed view (without token)
        email_confirmed_url = reverse('email_confirmed', kwargs={'uidb64': self.uidb64, 'token': 111})[:-4]
        self.assertIn(email_confirmed_url, self.email.body)

class InvalidSignUpTests(TestCase):
    def setUp(self):
        url = reverse('signup')
        # submit not valid data (an empty dictionary)
        self.response = self.client.post(url, {})

    def test_signup_status_code(self):
        # An invalid form submission should return to the page with form again
        self.assertEquals(self.response.status_code, 200)

    def test_form_errors(self):
        # response should have a error info
        form = self.response.context.get('form')
        self.assertTrue(form.errors)

    def test_dont_create_user(self):
        # and no user created obviously
        self.assertFalse(RoomUser.objects.exists())