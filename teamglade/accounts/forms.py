from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext_lazy as _
from rooms.models import RoomUser, Room


class RoomUserCreationForm(UserCreationForm):
    email = forms.CharField(max_length=254, required=True, widget=forms.EmailInput())

    class Meta(UserCreationForm.Meta):
        #email = forms.CharField(max_length=254, required=True, widget=forms.EmailInput())
        model = RoomUser
        fields = ('username', 'email', 'password1', 'password2')
        #fields = UserCreationForm.Meta.fields + ('custom_field',) - adding fields don't working

    # def __init__(self, *args, **kwargs):
    #     super(RoomUserCreationForm, self).__init__(*args, **kwargs)
    #     self.fields['email'].required = True

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