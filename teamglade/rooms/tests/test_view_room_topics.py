from django.urls import reverse
from django.test import TestCase


class RoomViewTests(TestCase):
    def test_room_view_status_code(self):
        url = reverse('room')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

    def test_room_view_contains_navigation_links(self):
        homepage_url = reverse('home')
        roompage_url = reverse('room')
        response = self.client.get(roompage_url)
        self.assertContains(response, 'href="{0}"'.format(homepage_url))