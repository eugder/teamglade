from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse, resolve
from django.test import TestCase
from .views import signup
from ..rooms.models import RoomUser

class SignUpTests(TestCase):
    def setUp(self):
        self.url = reverse('signup')
        self.response = self.client.get(self.url)

    def test_sighnup_status_code(self):
        self.assertEquals(self.response.status_code, 200)

    def test_signup_url_resolves_signup_view(self):
        view = resolve(self.url)
        self.assertEquals(view.func, signup)

    def test_csrf(self):
        self.assertContains(self.response, 'csrfmiddlewaretoken')

    def test_contains_form(self):
        form = self.response.context.get('form')
        self.assertIsInstance(form, UserCreationForm)

class SuccessfulSignUpTests(TestCase):
    def setUp(self):
        url = reverse('signup')
        data = {
            'username': 'john',
            'email': 'john@doe.com',
            'password1': 'abcdef123456',
            'password2': 'abcdef123456'
        }
        self.response = self.client.post(url, data)
        self.home_url = reverse('home')

    def test_redirection(self):
        # A valid form submission should redirect the user to the home page
        # (302 code, 200 code means not correct filled data in form in setUp)
        self.assertRedirects(self.response, self.home_url)

    def test_user_creation(self):
        self.assertTrue(RoomUser.objects.exists())