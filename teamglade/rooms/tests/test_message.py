from django.core import mail
from django.urls import reverse
from django.test import TestCase


class MessageViewTests(TestCase):
    def setUp(self):
        self.url = reverse('message')
        self.response = self.client.post(
            self.url, {
                'name': 'Test Name',
                'email': 'test@test.com',
                'phone': '1234',
                'message': 'Test Message',
            }
        )
        self.email = mail.outbox[0]

    def test_message_view_status_code(self):
        self.assertEquals(self.response.status_code, 200)

    def test_home_link(self):
        room_url = reverse('home')
        self.assertContains(self.response, room_url)

    def test_email_subject(self):
        self.assertEqual("Site visitor's message. [Test Name]", self.email.subject)

    def test_email_body(self):
        # has a message and phone number
        self.assertEqual("Test Message\n1234\ntest@test.com", self.email.body)


class HoneypotMessageTests(TestCase):
    def setUp(self):
        self.url = reverse('message')

    def test_honeypot_website_field_filled_blocks_submission(self):
        """Test that filling the 'website' honeypot field blocks the submission"""
        response = self.client.post(
            self.url, {
                'name': 'Bot Name',
                'email': 'bot@bot.com',
                'phone': '1234',
                'message': 'Bot Message',
                'website': 'http://spam.com',  # Honeypot field filled
                'email_confirmation': '',
            }
        )
        # Should redirect to home
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('home'))
        # No email should be sent
        self.assertEqual(len(mail.outbox), 0)

    def test_honeypot_email_confirmation_field_filled_blocks_submission(self):
        """Test that filling the 'email_confirmation' honeypot field blocks the submission"""
        response = self.client.post(
            self.url, {
                'name': 'Bot Name',
                'email': 'bot@bot.com',
                'phone': '1234',
                'message': 'Bot Message',
                'website': '',
                'email_confirmation': 'bot@bot.com',  # Honeypot field filled
            }
        )
        # Should redirect to home
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('home'))
        # No email should be sent
        self.assertEqual(len(mail.outbox), 0)

    def test_honeypot_both_fields_filled_blocks_submission(self):
        """Test that filling both honeypot fields blocks the submission"""
        response = self.client.post(
            self.url, {
                'name': 'Bot Name',
                'email': 'bot@bot.com',
                'phone': '1234',
                'message': 'Bot Message',
                'website': 'http://spam.com',
                'email_confirmation': 'bot@bot.com',
            }
        )
        # Should redirect to home
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('home'))
        # No email should be sent
        self.assertEqual(len(mail.outbox), 0)

    def test_honeypot_fields_empty_allows_submission(self):
        """Test that legitimate submission with empty honeypot fields works"""
        response = self.client.post(
            self.url, {
                'name': 'Real User',
                'email': 'user@user.com',
                'phone': '5678',
                'message': 'Real Message',
                'website': '',  # Empty honeypot
                'email_confirmation': '',  # Empty honeypot
            }
        )
        # Should render confirmation page
        self.assertEqual(response.status_code, 200)
        # Email should be sent
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "Site visitor's message. [Real User]")

    def test_honeypot_fields_missing_allows_submission(self):
        """Test that submission without honeypot fields in POST data works (backward compatibility)"""
        response = self.client.post(
            self.url, {
                'name': 'Real User',
                'email': 'user@user.com',
                'phone': '5678',
                'message': 'Real Message',
                # No honeypot fields at all
            }
        )
        # Should render confirmation page
        self.assertEqual(response.status_code, 200)
        # Email should be sent
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, "Site visitor's message. [Real User]")
