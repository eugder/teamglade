from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes


class EmailConfirmedViewTests(TestCase):
    """Test cases for the email_confirmed view"""

    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.user_model = get_user_model()

        # Create an inactive test user (as created during signup)
        self.test_user = self.user_model.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            is_active=False  # User starts inactive until email confirmed
        )

        # Generate valid token and uidb64
        self.token = default_token_generator.make_token(self.test_user)
        self.uidb64 = urlsafe_base64_encode(force_bytes(self.test_user.pk))

    def test_email_confirmed_valid_token_activates_user(self):
        """Test valid token and uidb64 activates user and shows success page"""
        url = reverse('email_confirmed', kwargs={'uidb64': self.uidb64, 'token': self.token})
        response = self.client.get(url)

        # Refresh user from database
        self.test_user.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'email_confirmed.html')
        self.assertTrue(self.test_user.is_active)

    def test_email_confirmed_invalid_token_shows_error(self):
        """Test invalid token shows error page and doesn't activate user"""
        invalid_token = 'invalid-token-string'
        url = reverse('email_confirmed', kwargs={'uidb64': self.uidb64, 'token': invalid_token})
        response = self.client.get(url)

        # Refresh user from database
        self.test_user.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'email_not_confirmed.html')
        self.assertFalse(self.test_user.is_active)
        self.assertEqual(response.context['context'], self.uidb64)

    def test_email_confirmed_invalid_uidb64_shows_error(self):
        """Test invalid uidb64 shows error page"""
        invalid_uidb64 = 'invalid-uidb64'
        url = reverse('email_confirmed', kwargs={'uidb64': invalid_uidb64, 'token': self.token})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'email_not_confirmed.html')
        self.assertEqual(response.context['context'], invalid_uidb64)

    def test_email_confirmed_nonexistent_user_shows_error(self):
        """Test uidb64 for non-existent user shows error page"""
        # Create uidb64 for non-existent user ID
        fake_user_id = 99999
        fake_uidb64 = urlsafe_base64_encode(force_bytes(fake_user_id))
        url = reverse('email_confirmed', kwargs={'uidb64': fake_uidb64, 'token': self.token})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'email_not_confirmed.html')

    def test_email_confirmed_already_active_user_still_works(self):
        """Test confirmation works even if user is already active"""
        # Activate user first
        self.test_user.is_active = True
        self.test_user.save()

        # Generate new token for active user
        token = default_token_generator.make_token(self.test_user)
        url = reverse('email_confirmed', kwargs={'uidb64': self.uidb64, 'token': token})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'email_confirmed.html')

    def test_email_confirmed_success_template_content(self):
        """Test success template contains expected elements"""
        url = reverse('email_confirmed', kwargs={'uidb64': self.uidb64, 'token': self.token})
        response = self.client.get(url)

        self.assertContains(response, 'Email address confirmed')
        self.assertContains(response, 'successfully confirmed')
        self.assertContains(response, reverse('login'))
        self.assertContains(response, 'check-circle.svg')

    def test_email_confirmed_error_template_content(self):
        """Test error template contains expected elements and resend link"""
        invalid_token = 'invalid-token'
        url = reverse('email_confirmed', kwargs={'uidb64': self.uidb64, 'token': invalid_token})
        response = self.client.get(url)

        self.assertContains(response, 'Email verification failed')
        self.assertContains(response, 'invalid or has expired')
        self.assertContains(response, reverse('email_resend', kwargs={'uidb64': self.uidb64}))
        self.assertContains(response, 'error-circle.svg')

    def test_email_confirmed_post_method_works(self):
        """Test POST request works same as GET"""
        url = reverse('email_confirmed', kwargs={'uidb64': self.uidb64, 'token': self.token})

        get_response = self.client.get(url)

        # Reset user to inactive for POST test
        self.test_user.is_active = False
        self.test_user.save()

        # Generate new token since the previous one was used
        new_token = default_token_generator.make_token(self.test_user)
        post_url = reverse('email_confirmed', kwargs={'uidb64': self.uidb64, 'token': new_token})
        post_response = self.client.post(post_url)

        self.assertEqual(get_response.status_code, 200)
        self.assertEqual(post_response.status_code, 200)

        # Both should render the same template (email_confirmed.html for valid tokens)
        self.assertTemplateUsed(get_response, 'email_confirmed.html')
        self.assertTemplateUsed(post_response, 'email_confirmed.html')

    def test_email_confirmed_user_activation_is_persistent(self):
        """Test user remains active after confirmation"""
        url = reverse('email_confirmed', kwargs={'uidb64': self.uidb64, 'token': self.token})
        self.client.get(url)

        # Check user is still active after some time/operations
        self.test_user.refresh_from_db()
        self.assertTrue(self.test_user.is_active)

        # Simulate user doing other operations
        self.test_user.email = 'newemail@example.com'
        self.test_user.save()

        # User should still be active
        self.test_user.refresh_from_db()
        self.assertTrue(self.test_user.is_active)