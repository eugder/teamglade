from django.test import TestCase
from ..forms import RoomUserCreationForm

class SignUpFormTest(TestCase):
    def test_form_has_fields(self):
        # Form has all fields
        form = RoomUserCreationForm()
        expected = ['username', 'email', 'password1', 'password2', 'website', 'phone', 'timestamp',]
        actual = list(form.fields)
        self.assertSequenceEqual(expected, actual)