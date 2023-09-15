from django.urls import reverse
from django.test import TestCase

class SignUpTests(TestCase):
    def test_sighnup_status_code(self):
        url = reverse('signup')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
