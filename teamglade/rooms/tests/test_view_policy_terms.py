from django.urls import reverse
from django.test import TestCase


class PolicyViewTests(TestCase):
    def test_policy_view_status_code(self):
        url = reverse('policy')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

    def test_policy_view_uses_correct_template(self):
        url = reverse('policy')
        response = self.client.get(url)
        self.assertTemplateUsed(response, 'privacy_policy.html')


class TermsViewTests(TestCase):
    def test_terms_view_status_code(self):
        url = reverse('terms')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

    def test_terms_view_uses_correct_template(self):
        url = reverse('terms')
        response = self.client.get(url)
        self.assertTemplateUsed(response, 'terms_conditions.html')
