from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.core import mail
from django.urls import reverse
from django.test import TestCase
from django.test.client import Client
from django.utils import timezone
from django.conf import settings
from ..models import CustomField, Queue, Ticket
from urllib.parse import urlparse
from ..user import HelpdeskUser
from ..views import staff


class TicketUpdateTestCase(TestCase):
    fixtures = ['emailtemplate.json']

    def setUp(self):
        self.queue_public = Queue.objects.create(
            title='Queue 1',
            slug='q1',
            allow_public_submission=True,
            new_ticket_cc='new.public@example.com',
            updated_ticket_cc='update.public@example.com'
        )

        self.queue_private = Queue.objects.create(
            title='Queue 2',
            slug='q2',
            allow_public_submission=False,
            new_ticket_cc='new.private@example.com',
            updated_ticket_cc='update.private@example.com'
        )

        self.ticket_data = {
            'title': 'Test Ticket',
            'description': 'Some Test Ticket',
        }

        self.client = Client()

    def loginUser(self, is_staff=True):
        """Create a staff user and login"""
        User = get_user_model()
        self.user = User.objects.create(
            username='User_1',
            is_staff=is_staff,
        )
        self.user.set_password('pass')
        self.user.save()
        self.client.login(username='User_1', password='pass')

    def test_ticket_update(self):
        self.loginUser()

        User = get_user_model()
        self.user2 = User.objects.create(
            username='User_2',
            is_staff=True,
        )

        initial_data = {
            'title': 'Private ticket test',
            'queue': self.queue_public,
            'assigned_to': self.user,
            'status': Ticket.OPEN_STATUS,
        }

        ticket = Ticket.objects.create(**initial_data)
        ticket_id = ticket.id
        ticket.assigned_to = self.user

        post_data = {
            "owner": self.user2.id,
        }

        response = self.client.post(reverse('supportSystem:update', kwargs={'ticket_id': ticket_id}), post_data, follow=True)
        self.assertContains(response, 'Changed Savinikas from User_1 to User_2')

