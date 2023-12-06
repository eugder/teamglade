from django.core import mail
from django.urls import reverse, resolve
from django.test import TestCase
from ..models import Room, Topic, RoomUser
from ..views import SendInviteView
from ..forms import SendInviteForm


class SendInviteViewTestCase(TestCase):
    def setUp(self):
        user = RoomUser.objects.create_user(username='usr', email='usr@test.com', password='111')
        room_obj = Room.objects.create(name='Room name', created_by=user)
        topic_obj = Topic.objects.create(title='Test title', message='Test message', created_by=user, room=room_obj)
        self.client.login(username='usr', password='111')  # topic view has a @login_required
        self.url = reverse('send_invite', kwargs={'pk': 1})
        self.response = self.client.get(self.url)


class SendInviteViewTests(SendInviteViewTestCase):
    def test_send_invite_view_status_code(self):
        self.assertEquals(self.response.status_code, 200)

    def test_url_resolves_correct_view(self):
        view = resolve(self.url)
        self.assertEquals(view.func.view_class, SendInviteView)

    def test_csrf(self):
        self.assertContains(self.response, 'csrfmiddlewaretoken')

    def test_contains_form(self):
        form = self.response.context.get('form')
        self.assertIsInstance(form, SendInviteForm)


class LoginRequiredSendInviteViewTests(SendInviteViewTestCase):
    def setUp(self):
        super().setUp()
        self.client.logout()

    def test_redirection(self):
        login_url = reverse('login')
        response = self.client.get(self.url)
        self.assertRedirects(response, '{login_url}?next={url}'.format(login_url=login_url, url=self.url))


class SuccessfulSendInviteViewTests(SendInviteViewTestCase):
    def setUp(self):
        super().setUp()
        self.email_to = 'test@test.com'
        self.response = self.client.post(self.url, {'email': self.email_to})
        self.email = mail.outbox[0]

    def test_email_subject(self):
        self.assertEqual('[TeamGlade] You are invited to join TeamGlade room', self.email.subject)

    def test_email_body(self):
        # has a link with code (8 symbols)
        self.assertRegex(self.email.body, r'rooms/invite/[a-z0-9]{8}/')

    def test_invited_user(self):
        users = RoomUser.objects.all()
        invited_user = users.last()
        self.assertEquals(len(users), 2)
        self.assertEquals(invited_user.username, self.email_to)
        self.assertEquals(invited_user.email, self.email_to)

    def test_redirection(self):
        '''
        A valid form submission should redirect the user
        '''
        room_url = reverse('room')
        self.assertRedirects(self.response, room_url)
