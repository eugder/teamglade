from django import forms
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views.generic import UpdateView
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

@method_decorator(login_required, name='dispatch')
class UserUpdateView(UpdateView):
    model = RoomUser
    fields = ('username', 'email', )
    template_name = 'my_account.html'
    success_url = reverse_lazy('my_account')

    def get_object(self):
        # let know UpdateView what exactly user is updating
        return self.request.user


def signup(request):
    if request.method == 'POST':
        form = RoomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()

            # all new users get a room
            new_room = Room.objects.create(
                name=str(user.username) + " room",
                created_by=user,
            )

            login(request, user)
            return redirect('home')
    else:
        form = RoomUserCreationForm()
    return render(request, 'signup.html', {'form': form})