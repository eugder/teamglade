#from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from rooms.models import RoomUser

class RoomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = RoomUser
        #fields = UserCreationForm.Meta.fields + ('custom_field',) - adding fields don't working

def signup(request):
    if request.method == 'POST':
        form = RoomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            #login(request, user)
            return redirect('home')
    else:
        form = RoomUserCreationForm()
    return render(request, 'signup.html', {'form': form})