from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from supportSystem.models import Ticket, Queue


User = get_user_model()

class TicketSearchTestCase(TestCase):
    def setUp(self):
        q = Queue(title='o365 support', slug='o365-support')
        q.save()
        t = Ticket(title='TVery big problem!', submitter_email='mikas.krukauskas@squalio.com')
        t.queue = q
        t.save()
        self.ticket = t

    def test_ticket_search(self):
        t = Ticket.objects.get(id=self.ticket.id)
        self.assertEqual(t.title, self.ticket.title)
        self.assertEqual(t.submitter_email, self.ticket.submitter_email)
