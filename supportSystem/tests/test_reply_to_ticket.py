from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from django.test.client import Client
from ..models import  Queue, Ticket
class TicketReplytestCase(TestCase):
    fixtures = ['emailtemplate.json']

    def setUp(self):
        self.queue_public = Queue.objects.create(
            title='Queue 1',
            slug='q1',
            allow_public_submission=True,
            new_ticket_cc='new.public@example.com',
            updated_ticket_cc='update.public@example.com'
        )

        self.ticket_data = {
            'title': 'Test Ticket',
            'description': 'Some Test Ticket',
        }

        self.client = Client()

    def loginUser(self, is_staff=True):
        User = get_user_model()
        self.user = User.objects.create(
            username='User_1',
            is_staff=is_staff,
        )
        self.user.set_password('pass')
        self.user.save()
        self.client.login(username='User_1', password='pass')

    def test_ticket_reply(self):
        self.loginUser()

        initial_data = {
            'title': 'Reply to ticket ticket test',
            'queue': self.queue_public,
            'assigned_to': self.user,
            'status': Ticket.OPEN_STATUS,
        }

        ticket = Ticket.objects.create(**initial_data)
        ticket_id = ticket.id
        ticket.assigned_to = self.user

        post_data = {
            "comment": "we are reviewing you ticket",
            "public": True,
        }

        response = self.client.post(reverse('supportSystem:update', kwargs={'ticket_id': ticket_id}), post_data, follow=True)
        self.assertContains(response, 'we are reviewing you ticket')
        self.assertContains(response, 'public')
