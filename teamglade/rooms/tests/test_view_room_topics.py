from django.urls import reverse, resolve
from django.test import TestCase
from ..models import Room, RoomUser
from ..views import room


class RoomViewTests(TestCase):
    def setUp(self):
        user = RoomUser.objects.create_user(username='usr', email='usr@test.com', password='111')
        room_obj = Room.objects.create(name='Room name', created_by=user)
        self.client.login(username='usr', password='111')  # room view has a @login_required
        self.url = reverse('room')
        self.response = self.client.get(self.url)

    def test_room_view_status_code(self):
        self.assertEquals(self.response.status_code, 200)

    def test_room_view_contains_navigation_links(self):
        homepage_url = reverse('home')
        self.assertContains(self.response, 'href="{0}"'.format(homepage_url))

    def test_url_resolves_correct_view(self):
        view = resolve(self.url)
        self.assertEquals(view.func, room)
