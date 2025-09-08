import time
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from rooms.models import RoomUser, Room


class RoomUserCreationForm(UserCreationForm):

    email = forms.CharField(
        max_length=254,
        required=True,
        widget=forms.EmailInput()
    )

    # Honeypot fields - website and phone
    website = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'honeypot-field',
            'tabindex': '-1',
            'autocomplete': 'off'
        })
    )

    phone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'honeypot-field',
            'tabindex': '-1',
            'autocomplete': 'off'
        })
    )

    # Time-based honeypot (hidden field to track form load time)
    timestamp = forms.CharField(
        widget=forms.HiddenInput(),
        required=False
    )

    class Meta(UserCreationForm.Meta):
        model = RoomUser
        fields = ('username', 'email', 'password1', 'password2', 'website', 'phone', 'timestamp')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set timestamp when form is initialized
        if not self.is_bound:
            self.fields['timestamp'].initial = str(int(time.time()))

    def clean_website(self):
        """Honeypot validation - this field should be empty"""
        website = self.cleaned_data.get('website')
        if website:
            raise ValidationError('Spam detected. Please try again.')
        return website

    def clean_phone(self):
        """Honeypot validation - this field should be empty"""
        phone = self.cleaned_data.get('phone')
        if phone:
            raise ValidationError('Spam detected. Please try again.')
        return phone

    def clean_timestamp(self):
        """Time-based validation - form should take reasonable time to fill"""
        timestamp = self.cleaned_data.get('timestamp')
        if timestamp:
            try:
                form_load_time = int(timestamp)
                current_time = int(time.time())
                time_taken = current_time - form_load_time

                # Form filled too quickly (less than 3 seconds) - likely a bot
                if time_taken < 3:
                    raise ValidationError('Form submitted too quickly. Please try again.')

                # Form took too long (more than 30 minutes) - might be suspicious
                if time_taken > 1800:  # 30 minutes
                    raise ValidationError('Form session expired. Please refresh and try again.')

            except (ValueError, TypeError):
                raise ValidationError('Invalid form data. Please try again.')

        return timestamp


class UserUpdateForm(forms.ModelForm):
    roomname = forms.CharField(
        max_length=30,
        label="Room name",
        help_text="30 characters or fewer.",
        required=False
    )

    class Meta:
        model = RoomUser
        fields = ['username', 'email']
        help_texts = {
            "email": _("Required. Valid email address."),
        }