import time
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
        self.response = self.client.get(
            self.url,
            HTTP_USER_AGENT='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36...',
            HTTP_ACCEPT='text/html,application/xhtml+xml,application/xml;q=0.9...',
            HTTP_ACCEPT_LANGUAGE='en-US,en;q=0.9',
        )

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
        # csrf, username, email, password1, password2 and honeypot fields website, phone and timestamp
        self.assertContains(self.response, '<input', 8)
        self.assertContains(self.response, 'type="text"', 3)
        self.assertContains(self.response, 'type="email"', 1)
        self.assertContains(self.response, 'type="password"', 2)

class SuccessfulSignUpTests(TestCase):
    def setUp(self):
        url = reverse('signup')
        data = {
            'username': 'john',
            'email': 'john@doe.com',
            'password1': 'abcdef123456',
            'password2': 'abcdef123456',
            'website': '', # honeypot
            'phone': '', # honeypot
        }
        # Create a new user with proper HTTP headers to avoid bot detection
        self.response = self.client.post(
            url,
            data,
            # Add headers that real browsers send
            HTTP_USER_AGENT='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            HTTP_ACCEPT='text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            HTTP_ACCEPT_LANGUAGE='en-US,en;q=0.9',
        )
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
        self.response = self.client.post(
            url,
            {},  # Empty data - should cause form validation errors
            # Add proper headers to avoid bot detection interference
            HTTP_USER_AGENT='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            HTTP_ACCEPT='text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            HTTP_ACCEPT_LANGUAGE='en-US,en;q=0.9',
        )

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

class HoneypotSignUpTests(TestCase):
    """
    Tests bot submissions where honeypot fields are filled.
    """
    def setUp(self):
        self.url = reverse('signup')
        self.base_data = {
            'username': 'botuser',
            'email': 'bot@spam.com',
            'password1': 'botpassword123',
            'password2': 'botpassword123',
        }
        self.headers = {
            'HTTP_USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36...',
            'HTTP_ACCEPT': 'text/html,application/xhtml+xml,application/xml;q=0.9...',
            'HTTP_ACCEPT_LANGUAGE': 'en-US,en;q=0.9',
        }

    def test_signup_with_website_honeypot_filled(self):
        """
        Tests that filling the 'website' honeypot field prevents registration.
        """
        data = self.base_data.copy()
        data['website'] = 'http://some-spam-site.com'  # Bot fills this field
        data['phone'] = ''

        response = self.client.post(self.url, data, **self.headers)

        # The form should be re-rendered with validation errors
        self.assertEquals(response.status_code, 200)
        # No user should be created
        self.assertFalse(RoomUser.objects.exists())
        # The form should contain a 'Spam detected' error
        form = response.context.get('form')
        self.assertTrue(form.errors)
        self.assertIn('Spam detected', str(form.errors))

    def test_signup_with_phone_honeypot_filled(self):
        """
        Tests that filling the 'phone' honeypot field prevents registration.
        """
        data = self.base_data.copy()
        data['website'] = ''
        data['phone'] = '123-456-7890'  # Bot fills this field

        response = self.client.post(self.url, data, **self.headers)

        # The form should be re-rendered with validation errors
        self.assertEquals(response.status_code, 200)
        # No user should be created
        self.assertFalse(RoomUser.objects.exists())
        # The form should contain a 'Spam detected' error
        form = response.context.get('form')
        self.assertTrue(form.errors)
        self.assertIn('Spam detected', str(form.errors))

class TimestampHoneypotSignUpTests(TestCase):
    """
    Tests bot submissions based on the timestamp honeypot field.
    """

    def setUp(self):
        self.url = reverse('signup')
        self.base_data = {
            'username': 'botuser',
            'email': 'bot@spam.com',
            'password1': 'botpassword123',
            'password2': 'botpassword123',
            'website': '',
            'phone': '',
        }
        self.headers = {
            'HTTP_USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36...',
            'HTTP_ACCEPT': 'text/html,application/xhtml+xml,application/xml;q=0.9...',
            'HTTP_ACCEPT_LANGUAGE': 'en-US,en;q=0.9',
        }

    def test_signup_submitted_too_quickly(self):
        """
        Tests that a form submitted too quickly (less than 3 seconds) is rejected.
        """
        data = self.base_data.copy()
        # Simulate an instant submission by setting the timestamp to the current time.
        # The clean_timestamp method will calculate the difference as < 3 seconds.
        data['timestamp'] = str(int(time.time()))

        response = self.client.post(self.url, data, **self.headers)

        self.assertEquals(response.status_code, 200)
        self.assertFalse(RoomUser.objects.exists())
        form = response.context.get('form')
        self.assertTrue(form.errors)
        self.assertIn('Form submitted too quickly', str(form.errors))

    def test_signup_submitted_too_slowly(self):
        """
        Tests that a form submitted after the session expires (more than 30 minutes) is rejected.
        """
        data = self.base_data.copy()
        # Simulate a very old form by setting the timestamp to 31 minutes (1860s) in the past.
        old_timestamp = int(time.time()) - 1860
        data['timestamp'] = str(old_timestamp)

        response = self.client.post(self.url, data, **self.headers)

        self.assertEquals(response.status_code, 200)
        self.assertFalse(RoomUser.objects.exists())
        form = response.context.get('form')
        self.assertTrue(form.errors)
        self.assertIn('Form session expired', str(form.errors))