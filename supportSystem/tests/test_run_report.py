from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from ..models import Queue, Ticket
from ..query import query_to_base64


class ReportsTestCase(TestCase):
    def setUp(self):
        self.queue = Queue.objects.create(
            title="Test queue",
            slug="test_queue",
            allow_public_submission=True,
        )
        self.queue.save()

        self.ticket1 = Ticket.objects.create(
            title="Test status and priority",
            queue=self.queue,
            description="lol",
            priority=2,
            status=Ticket.OPEN_STATUS,
        )
        self.ticket1.save()
        self.ticket2 = Ticket.objects.create(
            title="test priority",
            queue=self.queue,
            description="lol",
            priority=2,
            status=Ticket.OPEN_STATUS,
        )
        self.ticket2.save()

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

    def test_generate_report(self):
        self.loginUser()
        report = 'queuestatus'

        response = self.client.get(reverse('supportSystem:run_report', kwargs={'report': 'queuestatus'}), follow=True)

