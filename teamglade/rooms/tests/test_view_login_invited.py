from django.urls import reverse, resolve
from django.test import TestCase
from ..models import Room, RoomUser
from ..views import LoginInvitedView


class LoginInvitedViewTestCase(TestCase):
    def setUp(self):
        code = '111'
        self.user = RoomUser.objects.create_user(
            username='usr@test.com',
            email='usr@test.com',
            password=code,
            invite_code=code,
        )
        room_obj = Room.objects.create(name='Room name', created_by=self.user)
        self.url = reverse('login_invite', kwargs={'code': code})
        self.response = self.client.get(self.url)

    def test_url_resolves_correct_view(self):
        view = resolve(self.url)
        self.assertEquals(view.func.view_class, LoginInvitedView)

    def test_logged_in_invited_user(self):
        self.assertTrue(self.user.is_authenticated)

    def test_redirection(self):
        # A successful login invited user should redirect
        room_url = reverse('room')
        self.assertRedirects(self.response, room_url)
