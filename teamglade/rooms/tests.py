from django.urls import reverse
from django.test import TestCase
from .models import Room, Topic, RoomUser

class HomeViewTests(TestCase):
    def test_home_view_status_code(self):
        url = reverse('home')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

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

class NewTopicTests(TestCase):
    def setUp(self):
        user = RoomUser.objects.create_user(username='usr', email='usr@test.com', password='111')
        Room.objects.create(name='Room name', created_by=user)

    # def test_new_topic_view_status_code(self):
    #     url = reverse('new_topic', kwargs={'pk': 1})
    #     responce = self.client.get(url)
    #     self.assertEquals(responce.status_code, 200)

    def test_new_topic_view_status_code2(self):
        url = reverse('new_topic', kwargs={'pk': 99})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 404)

    def test_mscrf(self):
        url = reverse('new_topic', kwargs={'pk': 1})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, 'csrfmiddlewaretoken')

    # def test_new_topic_valid_post_data(self):
    #     url = reverse('new_topic', kwargs={'pk': 1})
    #     data = {'title': 'Test title', 'message': 'Test Message'}
    #     response = self.client.post(url, data)
    #     self.assertTrue(Topic.objects.exists())
