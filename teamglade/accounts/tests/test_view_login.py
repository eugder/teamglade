from django.contrib.auth.forms import AuthenticationForm
from django.urls import reverse, resolve
from django.test import TestCase
from django.contrib.auth import views as auth_views
from rooms.models import RoomUser, Room


class LoginViewTests(TestCase):
    """
    Tests for the basic login view (GET request).
    """
    def setUp(self):
        # Get the login page
        self.url = reverse('login')
        self.response = self.client.get(self.url)

    def test_login_status_code(self):
        """
        Tests that the login page returns a 200 status code.
        """
        self.assertEquals(self.response.status_code, 200)

    def test_login_url_resolves_login_view(self):
        """
        Tests that the 'login' URL resolves to Django's LoginView.
        """
        view = resolve(self.url)
        self.assertEquals(view.func.__name__, auth_views.LoginView.as_view().__name__)

    def test_csrf(self):
        """
        Tests that the response contains a CSRF token.
        """
        self.assertContains(self.response, 'csrfmiddlewaretoken')

    def test_contains_form(self):
        """
        Tests that the response contains the correct form (AuthenticationForm).
        """
        form = self.response.context.get('form')
        self.assertIsInstance(form, AuthenticationForm)

    def test_form_inputs(self):
        """
        Tests that the view contains the expected inputs:
        - csrf token (hidden)
        - csrfmiddlewaretoken (hidden)
        - username field (text input)
        - password field (password input)
        """
        # Should contain: 2 csrf-related inputs + username + password = 4 inputs
        self.assertContains(self.response, '<input', 4)
        self.assertContains(self.response, 'type="text"', 1)
        self.assertContains(self.response, 'type="password"', 1)


class SuccessfulLoginTests(TestCase):
    """
    Tests for successful login with valid credentials.
    """
    def setUp(self):
        # Create an active user with a room
        self.username = 'testuser'
        self.password = 'testpass123'
        self.user = RoomUser.objects.create_user(
            username=self.username,
            email='testuser@example.com',
            password=self.password,
            is_active=True  # Must be active to login
        )
        # Create a room for the user
        self.room = Room.objects.create(
            name=f"{self.username} room",
            created_by=self.user
        )

        self.url = reverse('login')
        self.room_url = reverse('room')

    def test_successful_login_redirects_to_room(self):
        """
        Tests that a successful login redirects to the 'room' page (LOGIN_REDIRECT_URL).
        """
        response = self.client.post(self.url, {
            'username': self.username,
            'password': self.password,
        })

        # Should redirect to 'room' page (302 status)
        self.assertRedirects(response, self.room_url)

    def test_user_is_authenticated_after_login(self):
        """
        Tests that the user is authenticated after a successful login.
        """
        self.client.post(self.url, {
            'username': self.username,
            'password': self.password,
        })

        # Make a new request to verify authentication
        response = self.client.get(self.room_url)
        user = response.context.get('user')

        self.assertTrue(user.is_authenticated)
        self.assertEquals(user.username, self.username)

    def test_login_with_next_parameter(self):
        """
        Tests that login redirects to the 'next' URL parameter if provided.
        """
        next_url = reverse('my_account')
        response = self.client.post(f"{self.url}?next={next_url}", {
            'username': self.username,
            'password': self.password,
        })

        # Should redirect to the 'next' URL
        self.assertRedirects(response, next_url)

    def test_login_case_sensitivity(self):
        """
        Tests that usernames are case-sensitive (Django default behavior).
        """
        # Try logging in with uppercase username
        response = self.client.post(self.url, {
            'username': self.username.upper(),
            'password': self.password,
        })

        # Should fail - username is case-sensitive
        self.assertEquals(response.status_code, 200)
        form = response.context.get('form')
        self.assertTrue(form.errors)


class FailedLoginTests(TestCase):
    """
    Tests for failed login attempts with invalid credentials.
    """
    def setUp(self):
        # Create an active user
        self.username = 'testuser'
        self.password = 'testpass123'
        self.user = RoomUser.objects.create_user(
            username=self.username,
            email='testuser@example.com',
            password=self.password,
            is_active=True
        )
        # Create a room for the user
        self.room = Room.objects.create(
            name=f"{self.username} room",
            created_by=self.user
        )

        self.url = reverse('login')

    def test_login_with_wrong_password(self):
        """
        Tests that login fails with a wrong password.
        """
        response = self.client.post(self.url, {
            'username': self.username,
            'password': 'wrongpassword',
        })

        # Should stay on login page (status 200)
        self.assertEquals(response.status_code, 200)

        # Form should have errors
        form = response.context.get('form')
        self.assertTrue(form.errors)

    def test_login_with_nonexistent_username(self):
        """
        Tests that login fails with a username that doesn't exist.
        """
        response = self.client.post(self.url, {
            'username': 'nonexistentuser',
            'password': 'somepassword',
        })

        # Should stay on login page
        self.assertEquals(response.status_code, 200)

        # Form should have errors
        form = response.context.get('form')
        self.assertTrue(form.errors)

    def test_login_with_empty_fields(self):
        """
        Tests that login fails when both fields are empty.
        """
        response = self.client.post(self.url, {
            'username': '',
            'password': '',
        })

        # Should stay on login page
        self.assertEquals(response.status_code, 200)

        # Form should have errors
        form = response.context.get('form')
        self.assertTrue(form.errors)
        # Both fields should have errors
        self.assertIn('username', form.errors)
        self.assertIn('password', form.errors)

    def test_login_with_only_username(self):
        """
        Tests that login fails when only username is provided.
        """
        response = self.client.post(self.url, {
            'username': self.username,
            'password': '',
        })

        # Should stay on login page
        self.assertEquals(response.status_code, 200)

        # Form should have password error
        form = response.context.get('form')
        self.assertTrue(form.errors)
        self.assertIn('password', form.errors)

    def test_login_with_only_password(self):
        """
        Tests that login fails when only password is provided.
        """
        response = self.client.post(self.url, {
            'username': '',
            'password': self.password,
        })

        # Should stay on login page
        self.assertEquals(response.status_code, 200)

        # Form should have username error
        form = response.context.get('form')
        self.assertTrue(form.errors)
        self.assertIn('username', form.errors)

    def test_user_not_authenticated_after_failed_login(self):
        """
        Tests that the user is not authenticated after a failed login attempt.
        """
        self.client.post(self.url, {
            'username': self.username,
            'password': 'wrongpassword',
        })

        # Make a new request
        response = self.client.get(reverse('home'))
        user = response.context.get('user')

        # User should still be anonymous
        self.assertFalse(user.is_authenticated)
        self.assertTrue(user.is_anonymous)


class InactiveUserLoginTests(TestCase):
    """
    Tests for login attempts with inactive users (users who haven't confirmed their email).
    """
    def setUp(self):
        # Create an INACTIVE user (email not confirmed)
        self.username = 'inactiveuser'
        self.password = 'testpass123'
        self.user = RoomUser.objects.create_user(
            username=self.username,
            email='inactive@example.com',
            password=self.password,
            is_active=False  # User hasn't confirmed email yet
        )
        # Create a room for the user
        self.room = Room.objects.create(
            name=f"{self.username} room",
            created_by=self.user
        )

        self.url = reverse('login')

    def test_inactive_user_cannot_login(self):
        """
        Tests that inactive users cannot login even with correct credentials.
        """
        response = self.client.post(self.url, {
            'username': self.username,
            'password': self.password,
        })

        # Should stay on login page
        self.assertEquals(response.status_code, 200)

        # Form should have errors
        form = response.context.get('form')
        self.assertTrue(form.errors)

    def test_inactive_user_not_authenticated(self):
        """
        Tests that inactive users are not authenticated after login attempt.
        """
        self.client.post(self.url, {
            'username': self.username,
            'password': self.password,
        })

        # Make a new request
        response = self.client.get(reverse('home'))
        user = response.context.get('user')

        # User should be anonymous
        self.assertFalse(user.is_authenticated)
        self.assertTrue(user.is_anonymous)


class LoginWithEmailTests(TestCase):
    """
    Tests to verify that users cannot login with email (Django default uses username only).
    """
    def setUp(self):
        # Create an active user
        self.username = 'testuser'
        self.email = 'testuser@example.com'
        self.password = 'testpass123'
        self.user = RoomUser.objects.create_user(
            username=self.username,
            email=self.email,
            password=self.password,
            is_active=True
        )
        # Create a room for the user
        self.room = Room.objects.create(
            name=f"{self.username} room",
            created_by=self.user
        )

        self.url = reverse('login')

    def test_cannot_login_with_email(self):
        """
        Tests that users cannot login using their email address instead of username.
        """
        response = self.client.post(self.url, {
            'username': self.email,  # Try to use email as username
            'password': self.password,
        })

        # Should fail - Django's AuthenticationForm expects username, not email
        self.assertEquals(response.status_code, 200)
        form = response.context.get('form')
        self.assertTrue(form.errors)
