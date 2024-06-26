from pathlib import Path
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

    def test_new_topic_view_status_code_not_found(self):
        url = reverse('new_topic', kwargs={'pk': 99})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 404)

    def test_new_topic_view_no_permission(self):
        user2 = RoomUser.objects.create_user(username='usr2', email='usr2@test.com', password='222')
        room_obj2 = Room.objects.create(name='Room name', created_by=user2)
        url = reverse('new_topic', kwargs={'pk': room_obj2.pk})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 404)

    def test_mscrf(self):
        url = reverse('new_topic', kwargs={'pk': self.room.pk})
        response = self.client.get(url)
        self.assertContains(response, 'csrfmiddlewaretoken')

    def test_new_topic_valid_post_data(self):
        url = reverse('new_topic', kwargs={'pk': self.room.pk})

        # files attached to the topic
        f1 = open("rooms/tests/Upload_Test_File_1.txt")
        f2 = open("rooms/tests/Upload_Test_File_2.txt")
        files = [f1, f2]

        data = {'title': 'Test title', 'message': 'Test Message', 'files': files}
        self.client.post(url, data)
        f1.close()
        f2.close()

        self.assertTrue(Topic.objects.exists())
        self.assertTrue(Path("media/uploads/Upload_Test_File_1.txt").exists())
        self.assertTrue(Path("media/uploads/Upload_Test_File_2.txt").exists())

    def tearDown(self):
        # removing uploaded files (if exist)
        p1 = Path("media/uploads/Upload_Test_File_1.txt")
        p1.unlink(missing_ok=True)
        p2 = Path("media/uploads/Upload_Test_File_2.txt")
        p2.unlink(missing_ok=True)


class LoginRequiredNewTopicTests(TestCase):
    def setUp(self):
        user = RoomUser.objects.create_user(username='usr', email='usr@test.com', password='111')
        self.room = Room.objects.create(name='Room name', created_by=user)
        self.url = reverse('new_topic', kwargs={'pk': self.room.pk})
        self.response = self.client.get(self.url)

    def test_redirection(self):
        login_url = reverse('login')
        self.assertRedirects(self.response, '{login_url}?next={url}'.format(login_url=login_url, url=self.url))
