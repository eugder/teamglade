from django.test import TestCase
from ..views import SendInviteForm

class SendInviteFormTest(TestCase):
    def test_form_has_fields(self):
        # Form has a field
        form = SendInviteForm()
        expected = ['email']
        actual = list(form.fields)
        self.assertSequenceEqual(expected, actual)