from django.urls import reverse, resolve
from django.test import TestCase
from ..models import Room, Topic, RoomUser
from ..views import DeleteTopicView


class DeleteTopicViewTests(TestCase):
    def setUp(self):
        user = RoomUser.objects.create_user(username='usr', email='usr@test.com', password='111')
        self.room_obj = Room.objects.create(name='Room name', created_by=user)
        self.topic_obj = Topic.objects.create(title='Test title', message='Test message', created_by=user, room=self.room_obj)
        self.client.login(username='usr', password='111')  # topic view has a @login_required
        self.url = reverse('delete_topic', kwargs={'pk': self.topic_obj.pk})
        self.response = self.client.get(self.url)

    def test_topic_delete_view_status_code(self):
        self.assertEquals(self.response.status_code, 200)

    def test_topic_delete_view_no_permission(self):
        # if user is not owner/invited of this room - no permission to delete in another's room
        user2 = RoomUser.objects.create_user(username='usr2', email='usr2@test.com', password='222')
        room_obj2 = Room.objects.create(name='Room name', created_by=user2)
        topic_obj2 = Topic.objects.create(title='Test title', message='Test message', created_by=user2, room=room_obj2)
        url = reverse('delete_topic', kwargs={'pk': topic_obj2.pk})
        response = self.client.post(url)
        self.assertEquals(response.status_code, 404)

    def test_topic_delete_view_no_permission2(self):
        # if user is not owner of this room (invited user), he can delete only own topics
        user2 = RoomUser.objects.create_user(username='usr2', email='usr2@test.com', password='222', member_of=self.room_obj)
        url = reverse('delete_topic', kwargs={'pk': self.topic_obj.pk})
        self.client.login(username='usr2', password='222')
        response = self.client.post(url)
        self.assertEquals(response.status_code, 404)

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
