from django import forms
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from rooms.models import RoomUser

class RoomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        email = forms.CharField(max_length=254, required=True, widget=forms.EmailInput())
        model = RoomUser
        fields = ('username', 'email', 'password1', 'password2')
        #fields = UserCreationForm.Meta.fields + ('custom_field',) - adding fields don't working

def signup(request):
    if request.method == 'POST':
        form = RoomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = RoomUserCreationForm()
    return render(request, 'signup.html', {'form': form})