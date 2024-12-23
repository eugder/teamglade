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
