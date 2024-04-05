from django.urls import reverse, resolve
from django.test import TestCase
from ..models import Room, Topic, RoomUser
from ..views import DeleteTopicView


class DeleteTopicViewTests(TestCase):
    def setUp(self):
        user = RoomUser.objects.create_user(username='usr', email='usr@test.com', password='111')
        room_obj = Room.objects.create(name='Room name', created_by=user)
        self.topic_obj = Topic.objects.create(title='Test title', message='Test message', created_by=user, room=room_obj)
        self.client.login(username='usr', password='111')  # topic view has a @login_required
        self.url = reverse('delete_topic', kwargs={'pk': self.topic_obj.pk})
        self.response = self.client.get(self.url)

    def test_topic_delete_view_status_code(self):
        self.assertEquals(self.response.status_code, 200)

    def test_mscrf(self):
        self.assertContains(self.response, 'csrfmiddlewaretoken')

    def test_url_resolves_correct_view(self):
        view = resolve(self.url)
        self.assertEquals(view.func.view_class, DeleteTopicView)

    def test_topic_delete(self):
        self.client.post(self.url)
        self.assertFalse(Topic.objects.exists())


class LoginRequiredTopicTests(TestCase):
    def setUp(self):
        self.url = reverse('delete_topic', kwargs={'pk': 1})
        self.response = self.client.get(self.url)

    def test_redirection(self):
        login_url = reverse('login')
        self.assertRedirects(self.response, '{login_url}?next={url}'.format(login_url=login_url, url=self.url))
