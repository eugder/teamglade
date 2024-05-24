from django.test import TestCase
from ..forms import UserUpdateForm

class UserUpdateFormTest(TestCase):
    def test_form_has_fields(self):
        # Form has all fields
        form = UserUpdateForm()
        expected = ['username', 'email', 'roomname',]
        actual = list(form.fields)
        self.assertSequenceEqual(expected, actual)