from django.urls import reverse
from django.test import TestCase

class SignUpTests(TestCase):
    def setUp(self):
        url = reverse('signup')
        self.response = self.client.get(url)

    def test_sighnup_status_code(self):
        self.assertEquals(self.response.status_code, 200)
