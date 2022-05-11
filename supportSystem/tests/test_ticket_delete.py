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


class TicketDeleteTestCase(TestCase):
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


    def test_delete_ticket_staff(self):
        self.loginUser()
        ticket_data = dict(queue=self.queue_public, **self.ticket_data)
        ticket = Ticket.objects.create(**ticket_data)
        ticket_id = ticket.id
        response = self.client.get(reverse('supportSystem:delete', kwargs={'ticket_id': ticket_id}), follow=True)
        self.assertContains(response, 'Are you sure about deleting ticket?')
        response = self.client.post(reverse('supportSystem:delete', kwargs={'ticket_id': ticket_id}), follow=True)
        first_redirect = response.redirect_chain[0]
        first_redirect_url = first_redirect[0]
        urlparts = urlparse(first_redirect_url)
        self.assertEqual(urlparts.path, reverse('supportSystem:dashboard'))
        with self.assertRaises(Ticket.DoesNotExist):
            Ticket.objects.get(pk=ticket_id)




