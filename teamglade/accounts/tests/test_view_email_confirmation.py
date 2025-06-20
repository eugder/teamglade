from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes


class EmailConfirmationViewTests(TestCase):
    """Test cases for the email_confirmation view"""

    def setUp(self):
        """Set up test data"""
        self.client = Client()
        self.user_model = get_user_model()

        # Create a test user
        self.test_user = self.user_model.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

        # Generate uidb64 for testing
        self.uidb64 = urlsafe_base64_encode(force_bytes(self.test_user.pk))

    def test_email_confirmation_renders_correct_template_and_context(self):
        """Test view renders correct template with uidb64 in context"""
        url = reverse('email_confirmation', kwargs={'uidb64': self.uidb64})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'email_confirmation_sent.html')
        self.assertEqual(response.context['context'], self.uidb64)

    def test_email_confirmation_handles_invalid_uidb64(self):
        """Test view handles invalid uidb64 gracefully"""
        invalid_uidb64 = 'invalid-uidb64-string'
        url = reverse('email_confirmation', kwargs={'uidb64': invalid_uidb64})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['context'], invalid_uidb64)

    def test_email_confirmation_contains_required_template_elements(self):
        """Test rendered template contains expected content and links"""
        url = reverse('email_confirmation', kwargs={'uidb64': self.uidb64})
        response = self.client.get(url)

        self.assertContains(response, 'Check your mailbox!')
        self.assertContains(response, reverse('login'))
        self.assertContains(response, reverse('email_resend', kwargs={'uidb64': self.uidb64}))

    def test_email_confirmation_accessible_without_authentication(self):
        """Test view is accessible to unauthenticated users"""
        url = reverse('email_confirmation', kwargs={'uidb64': self.uidb64})
        response = self.client.get(url)

        # Should not redirect to login page
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'email_confirmation_sent.html')

    def test_email_confirmation_accepts_both_get_and_post(self):
        """Test view accepts both GET and POST methods"""
        url = reverse('email_confirmation', kwargs={'uidb64': self.uidb64})

        get_response = self.client.get(url)
        post_response = self.client.post(url)

        self.assertEqual(get_response.status_code, 200)
        self.assertEqual(post_response.status_code, 200)
        self.assertEqual(get_response.context['context'], post_response.context['context'])