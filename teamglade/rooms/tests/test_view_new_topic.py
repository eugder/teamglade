from django.urls import reverse
from django.test import TestCase
from ..models import Room, Topic, RoomUser


class NewTopicTests(TestCase):
    def setUp(self):
        user = RoomUser.objects.create_user(username='usr', email='usr@test.com', password='111')
        self.room = Room.objects.create(name='Room name', created_by=user)
        self.client.login(username='usr', password='111')  # new_topic view has a @login_required

    def test_new_topic_view_status_code(self):
        url = reverse('new_topic', kwargs={'pk': self.room.pk})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

    def test_new_topic_view_status_code2(self):
        url = reverse('new_topic', kwargs={'pk': 99})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 404)

    def test_mscrf(self):
        url = reverse('new_topic', kwargs={'pk': self.room.pk})
        response = self.client.get(url)
        self.assertContains(response, 'csrfmiddlewaretoken')

    def test_new_topic_valid_post_data(self):
        url = reverse('new_topic', kwargs={'pk': self.room.pk})
        data = {'title': 'Test title', 'message': 'Test Message'}
        self.client.post(url, data)
        self.assertTrue(Topic.objects.exists())


class LoginRequiredNewTopicTests(TestCase):
    def setUp(self):
        user = RoomUser.objects.create_user(username='usr', email='usr@test.com', password='111')
        self.room = Room.objects.create(name='Room name', created_by=user)
        self.url = reverse('new_topic', kwargs={'pk': self.room.pk})
        self.response = self.client.get(self.url)

    def test_redirection(self):
        login_url = reverse('login')
        self.assertRedirects(self.response, '{login_url}?next={url}'.format(login_url=login_url, url=self.url))