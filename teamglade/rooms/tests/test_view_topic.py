from django.urls import reverse, resolve
from django.test import TestCase
from ..models import Room, Topic, RoomUser
from ..views import topic


class TopicViewTests(TestCase):
    def setUp(self):
        user = RoomUser.objects.create_user(username='usr', email='usr@test.com', password='111')
        room_obj = Room.objects.create(name='Room name', created_by=user)
        topic_obj = Topic.objects.create(title='Test title', message='Test message', created_by=user, room=room_obj)
        self.client.login(username='usr', password='111')  # topic view has a @login_required
        self.url = reverse('topic', kwargs={'pk': topic_obj.pk})
        self.response = self.client.get(self.url)

    def test_topic_view_status_code(self):
        self.assertEquals(self.response.status_code, 200)

    def test_topic_view_no_permission(self):
        user2 = RoomUser.objects.create_user(username='usr2', email='usr2@test.com', password='222')
        room_obj2 = Room.objects.create(name='Room name', created_by=user2)
        topic_obj2 = Topic.objects.create(title='Test title', message='Test message', created_by=user2, room=room_obj2)
        url = reverse('topic', kwargs={'pk': topic_obj2.pk})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 404)

    def test_topic_view_contains_room_navigation_link(self):
        homepage_url = reverse('room')
        self.assertContains(self.response, 'href="{0}"'.format(homepage_url))

    def test_url_resolves_correct_view(self):
        view = resolve(self.url)
        self.assertEquals(view.func, topic)


class LoginRequiredTopicTests(TestCase):
    def setUp(self):
        self.url = reverse('topic', kwargs={'pk': 1})
        self.response = self.client.get(self.url)

    def test_redirection(self):
        login_url = reverse('login')
        self.assertRedirects(self.response, '{login_url}?next={url}'.format(login_url=login_url, url=self.url))
