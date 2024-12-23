from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views.generic import UpdateView
from rooms.models import RoomUser, Room
from .forms import RoomUserCreationForm, UserUpdateForm


@method_decorator(login_required, name='dispatch')
class UserUpdateView(UpdateView):
    template_name = 'my_account.html'
    form_class = UserUpdateForm

    def get_object(self):
        # let know UpdateView what exactly user is updating
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        user = self.request.user
        # if user is owner of this room he can edit room name, otherwise not
        if user.rooms.first() is not None:
            roomname_field = context['form'].fields["roomname"]
            roomname_field.initial = user.rooms.first().name
        else:
            roomname_field = context['form'].fields["roomname"]
            roomname_field.initial = user.member_of.name
            roomname_field.disabled = True
            roomname_field.help_text = "Invited users can't change room name"

        return context

    def form_valid(self, form):
        user = form.save()

        # if user is owner of this room - room name is saving, if invited user - not
        if user.rooms.first() is not None:
            room = user.rooms.first()
            room.name = form.cleaned_data['roomname']
            room.save()

        return HttpResponseRedirect(reverse('room'))


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
