from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core import mail
import time


class EmailResendViewTests(TestCase):
    """Test cases for the email_resend view"""

    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.user_model = get_user_model()

        # Create an inactive test user
        self.test_user = self.user_model.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            is_active=False
        )

        self.uidb64 = urlsafe_base64_encode(force_bytes(self.test_user.pk))

    def test_email_resend_valid_uidb64_sends_email(self):
        """Test resending email with valid uidb64 sends confirmation email"""
        url = reverse('email_resend', kwargs={'uidb64': self.uidb64})

        # Clear any existing emails
        mail.outbox = []

        response = self.client.get(url)

        # Should redirect to email_confirmation page
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('email_confirmation', kwargs={'uidb64': self.uidb64}))

        # Should send exactly one email
        self.assertEqual(len(mail.outbox), 1)

        # Verify email content
        sent_email = mail.outbox[0]
        self.assertEqual(sent_email.to, [self.test_user.email])
        self.assertIn('[TeamGlade] Confirm your email address', sent_email.subject)

    def test_email_resend_invalid_uidb64_raises_404(self):
        """Test resending email with invalid uidb64 returns 404 response"""
        invalid_uidb64 = 'invalid-uidb64-string'
        url = reverse('email_resend', kwargs={'uidb64': invalid_uidb64})

        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_email_resend_nonexistent_user_raises_404(self):
        """Test resending email for non-existent user raises Http404"""
        fake_user_id = 99999
        fake_uidb64 = urlsafe_base64_encode(force_bytes(fake_user_id))
        url = reverse('email_resend', kwargs={'uidb64': fake_uidb64})

        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)

    def test_email_resend_generates_new_token(self):
        """Test that resending email generates a new token each time"""
        url = reverse('email_resend', kwargs={'uidb64': self.uidb64})

        mail.outbox = []

        # Send first email
        self.client.get(url)
        first_email = mail.outbox[0]

        # Add small delay to ensure different timestamp
        time.sleep(1)  # 1s delay

        # Send second email
        self.client.get(url)
        second_email = mail.outbox[1]

        # Extract tokens from email content (they should be different)
        self.assertNotEqual(first_email.body, second_email.body)
        self.assertEqual(len(mail.outbox), 2)

    def test_email_resend_works_for_active_user(self):
        """Test email resend works even for already active users"""
        # Activate the user
        self.test_user.is_active = True
        self.test_user.save()

        url = reverse('email_resend', kwargs={'uidb64': self.uidb64})
        mail.outbox = []

        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(mail.outbox), 1)

    def test_email_resend_preserves_user_data(self):
        """Test that resending email doesn't modify user data"""
        original_username = self.test_user.username
        original_email = self.test_user.email
        original_is_active = self.test_user.is_active

        url = reverse('email_resend', kwargs={'uidb64': self.uidb64})
        self.client.get(url)

        # Refresh user from database
        self.test_user.refresh_from_db()

        # User data should remain unchanged
        self.assertEqual(self.test_user.username, original_username)
        self.assertEqual(self.test_user.email, original_email)
        self.assertEqual(self.test_user.is_active, original_is_active)

    def test_email_resend_rate_limiting_simulation(self):
        """Test multiple rapid resend requests work but could be rate limited"""
        url = reverse('email_resend', kwargs={'uidb64': self.uidb64})
        mail.outbox = []

        # Simulate rapid requests
        responses = []
        for i in range(5):
            response = self.client.get(url)
            responses.append(response)

        # All should redirect successfully (no built-in rate limiting in current implementation)
        for response in responses:
            self.assertEqual(response.status_code, 302)

        # Should send 5 emails
        self.assertEqual(len(mail.outbox), 5)

        # All emails should be to the same user
        for email in mail.outbox:
            self.assertEqual(email.to, [self.test_user.email])