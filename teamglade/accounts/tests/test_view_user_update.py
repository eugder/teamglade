from django.urls import reverse
from django.test import TestCase
from rooms.models import RoomUser, Room


class UserUpdateTests(TestCase):
    def setUp(self):
        user = RoomUser.objects.create_user(username='usr', email='usr@test.com', password='111')
        room = Room.objects.create(name='Test room', created_by=user)
        self.client.login(username='usr', password='111')  # new_topic view has a @login_required

    def test_user_update_view_status_code(self):
        url = reverse('my_account')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

    def test_mscrf(self):
        url = reverse('my_account')
        response = self.client.get(url)
        self.assertContains(response, 'csrfmiddlewaretoken')

    def test_user_update_valid_post_data(self):
        url = reverse('my_account')
        data = {'username': 'usr2', 'email': 'usr2@test.com', 'roomname' : 'Test room2'}
        self.client.post(url, data)
        self.assertEquals(RoomUser.objects.last().username, 'usr2')
        self.assertEquals(RoomUser.objects.last().email, 'usr2@test.com')
        self.assertEquals(Room.objects.last().name, 'Test room2')


class InvitedUserUpdateTests(TestCase):
    def setUp(self):
        user = RoomUser.objects.create_user(username='usr', email='usr@test.com', password='111')
        room = Room.objects.create(name='Test room', created_by=user)
        invited_user = RoomUser.objects.create_user(username='invited_usr', email='usr@test.com', password='111', member_of=room)
        self.client.login(username='invited_usr', password='111')  # new_topic view has a @login_required

    def test_invited_user_update_view_status_code(self):
        url = reverse('my_account')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

    def test_invited_user_update_valid_post_data(self):
        url = reverse('my_account')
        data = {'username': 'invited_usr2', 'email': 'usr2@test.com', 'roomname' : 'Test room2'}
        self.client.post(url, data)
        self.assertEquals(RoomUser.objects.last().username, 'invited_usr2')
        self.assertEquals(RoomUser.objects.last().email, 'usr2@test.com')
        self.assertEquals(Room.objects.last().name, 'Test room')

class LoginRequiredUserUpdateTests(TestCase):
    def setUp(self):
        user = RoomUser.objects.create_user(username='usr', email='usr@test.com', password='111')
        self.url = reverse('my_account')
        self.response = self.client.get(self.url)

    def test_redirection(self):
        login_url = reverse('login')
        self.assertRedirects(self.response, '{login_url}?next={url}'.format(login_url=login_url, url=self.url))
