from django.urls import reverse
from django.test import TestCase
from .models import Room, RoomUser

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

class NewTopicTests(TestCase):
    def setUp(self):
        user = RoomUser.objects.create_user(username='usr', email='usr@test.com', password='111')
        Room.objects.create(name='Room name', created_by=user)

    def test_new_topic_view_status_code(self):
        url = reverse('new_topic', kwargs={'pk': 1})
        responce = self.client.get(url)
        self.assertEquals(responce.status_code, 200)

    def test_new_topic_view_status_code2(self):
        url = reverse('new_topic', kwargs={'pk': 99})
        responce = self.client.get(url)
        self.assertEquals(responce.status_code, 404)