from django.urls import reverse
from django.test import TestCase

class HomeViewTests(TestCase):
    def test_home_view_status_code(self):
        url = reverse('home')
        responce = self.client.get(url)
        self.assertEquals(responce.status_code, 200)

class RoomViewTests(TestCase):
    def test_room_view_status_code(self):
        url = reverse('room')
        responce = self.client.get(url)
        self.assertEquals(responce.status_code, 200)

