from django.test import TestCase, override_settings
from django.core.management import call_command
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password

from supportSystem.models import Queue, Ticket, TicketCC, FollowUp, FollowUpAttachment
from supportSystem.management.commands.get_email import Command
import supportSystem.mail

import six
import itertools
from shutil import rmtree
import sys
import os
from tempfile import mkdtemp
import logging

from unittest import mock

THIS_DIR = os.path.dirname(os.path.abspath(__file__))

# class A addresses can't have first octet of 0
unrouted_socks_server = "0.0.0.1"
unrouted_email_server = "0.0.0.1"
# the last user port, reserved by IANA
unused_port = "49151"


class RegisterEmail(TestCase):
    def setUp(self):
        self.queue_public = Queue.objects.create()
        self.logger = logging.getLogger('supportSystem')

    def test_email_with_forwarded_message(self):
        with open(os.path.join(THIS_DIR, "files/test.eml")) as fd:
            test_email = fd.read()
        ticket = supportSystem.mail.object_from_message(test_email, self.queue_public, self.logger)
        self.assertEqual(ticket.title, "Testing email submission")
        self.assertEqual(ticket.description, "This is description of the ticket for testing purposes")
        self.assertEqual(ticket.submitter_email, "mikas.krukauskas@squalio.com")
