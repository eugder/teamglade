from django.urls import reverse
from django.test import TestCase

class RoomViewTests(TestCase):
    def test_room_view_status_code(self):
        url = reverse('room')
        responce = self.client.get(url)
        self.assertEquals(responce.status_code, 200)
