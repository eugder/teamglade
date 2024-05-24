from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy, reverse
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views.generic import UpdateView
from rooms.models import RoomUser, Room
from .forms import RoomUserCreationForm, UserUpdateForm


#----------------Teset update variant------------------------------
# class UserUpdateForm(forms.ModelForm):
#     room = forms.CharField(
#         widget=forms.Textarea(attrs={'rows': 5, 'placeholder': 'Your message'}),
#         label='Message',
#         max_length=1000,
#         help_text='The max length of the text is 1000.',
#     )
#
#     class Meta:
#         model = RoomUser
#         fields = ['username', 'email', 'room']
#
#
# def user_update(request):
#     if request.method == 'POST':
#         form = UserUpdateForm(request.POST)
#         if form.is_valid():
#             user = form.save()
#
#             return redirect('home')
#     else:
#         form = UserUpdateForm(instance=request.user)
#     return render(request, 'my_account.html', {'form': form})
#---------------------------------------------------------

#---Initial working variant without additional field---
# @method_decorator(login_required, name='dispatch')
# class UserUpdateView(UpdateView):
#     model = RoomUser
#     fields = ('username', 'email', )
#     template_name = 'my_account.html'
#     success_url = reverse_lazy('room')
#
#     # def get_context_data(self, **kwargs):
#     #     context = super(UserUpdateView, self).get_context_data(**kwargs)
#     #     context['second_model'] = Room.objects.get(id=1) #whatever you would like
#     #     return context
#
#     def get_object(self):
#         # let know UpdateView what exactly user is updating
#         return self.request.user


#---------------------------------------------------------


@method_decorator(login_required, name='dispatch')
class UserUpdateView(UpdateView):
    template_name = 'my_account.html'
    # context_object_name = 'form'
    form_class = UserUpdateForm
    # success_url = reverse_lazy('room')

    def get_object(self):
        # let know UpdateView what exactly user is updating
        return self.request.user

    def get_context_data(self, **kwargs):
        # context = super(UserUpdateView2, self).get_context_data(**kwargs)

        # context['form'] = ProfileUpdateForm2(instance=user, initial={'roomname': user.rooms.first().name})
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

        # context['form'].exclude = ('roomname',)
        # roomname_field.disabled = True
        # roomname_field.blank = True
        # roomname_field.required = False

        return context

    def form_valid(self, form):
        user = form.save()

        # if user is owner of this room - room name is saving, if invited user - not
        if user.rooms.first() is not None:
            room = user.rooms.first()
            room.name = form.cleaned_data['roomname']
            room.save()

        # profile.save()
        # return HttpResponseRedirect(reverse('users:user-profile', kwargs={'pk': self.get_object().id}))
        return HttpResponseRedirect(reverse('room'))
#---------------------------------------------------------
#----------------2-nd Teset update variant------------------------------
# class ProfileUpdateForm(forms.ModelForm):
#     username = forms.CharField(max_length=30)
#     email = forms.EmailField()
#     class Meta:
#         model = Room
#         fields = ['name']
#
# class UserSettings(LoginRequiredMixin, UpdateView):
#     template_name = 'my_account.html'
#     context_object_name = 'form'
#     # queryset = Room.objects.all()
#     form_class = ProfileUpdateForm
#
#     def get_object(self):
#         # let know UpdateView what exactly room is updating
#         return Room.objects.filter(pk=1).first()
#
#     def get_context_data(self, **kwargs):
#         context = super(UserSettings, self).get_context_data(**kwargs)
#         user = self.request.user
#         context['form'] = ProfileUpdateForm(instance=self.request.user.rooms.first(), initial={'username': user.username, 'email': user.email})
#         return context
#
#     def form_valid(self, form):
#         room = form.save()
#         user = room.created_by
#         user.username = form.cleaned_data['username']
#         user.email = form.cleaned_data['email']
#         user.save()
#         # profile.save()
#         # return HttpResponseRedirect(reverse('users:user-profile', kwargs={'pk': self.get_object().id}))
#         return HttpResponseRedirect(reverse('room'))
#
#     # def get_success_url(self):
#     #     return reverse('room')
#---------------------------------------------------------
#-------------Test sample --------------------------
# class ClientsUserForm(forms.ModelForm):
#     class Meta:
#         model = RoomUser
#         fields = ['username', 'email']
#
# class ClientsForm(forms.ModelForm):
#     class Meta:
#         model = Room
#         fields = ['name']
#
# class ClientUpdateView(UpdateView):
#     model = RoomUser
#     form_class = ClientsUserForm
#     second_form_class = ClientsForm
#     template_name = 'my_account.html'
#
#     def get_context_data(self, **kwargs):
#         context = super(ClientUpdateView, self).get_context_data(**kwargs)
#         context['active_client'] = True
#         if 'form' not in context:
#             context['form'] = self.form_class(self.request.GET, instance=self.request.user)
#         if 'form2' not in context:
#             context['form2'] = self.second_form_class(self.request.GET)
#         context['active_client'] = True
#         return context
#
#     def get_object(self):
#         # let know UpdateView what exactly user is updating
#         return self.request.user
#
#     def get(self, request, *args, **kwargs):
#         super(ClientUpdateView, self).get(request, *args, **kwargs)
#         form = self.form_class
#         form2 = self.second_form_class
#         return self.render_to_response(self.get_context_data(
#             object=self.object, form=form, form2=form2))
#
#     def post(self, request, *args, **kwargs):
#         self.object = self.get_object()
#         form = self.form_class(request.POST)
#         form2 = self.second_form_class(request.POST)
#
#         if form.is_valid() and form2.is_valid():
#             userdata = form.save(commit=False)
#             # used to set the password, but no longer necesarry
#             userdata.save()
#             employeedata = form2.save(commit=False)
#             employeedata.user = userdata
#             employeedata.save()
#             # messages.success(self.request, 'Settings saved successfully')
#             return HttpResponseRedirect(self.get_success_url())
#         else:
#             return self.render_to_response(
#               self.get_context_data(form=form, form2=form2))
#
#     def get_success_url(self):
#         return reverse('room')
#---------------------------------------------------------

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