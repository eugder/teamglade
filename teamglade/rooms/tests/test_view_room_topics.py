from django.urls import reverse
from django.test import TestCase
from ..models import Room, RoomUser


class RoomViewTests(TestCase):
    def setUp(self):
        user = RoomUser.objects.create_user(username='usr', email='usr@test.com', password='111')
        room = Room.objects.create(name='Room name', created_by=user)
        url = reverse('room', kwargs={'pk': room.pk})
        self.response = self.client.get(url)

    def test_room_view_status_code(self):
        self.assertEquals(self.response.status_code, 200)

    def test_room_view_contains_navigation_links(self):
        homepage_url = reverse('home')
        self.assertContains(self.response, 'href="{0}"'.format(homepage_url))