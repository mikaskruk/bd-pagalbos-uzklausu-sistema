from supportSystem.models import (
    Ticket,
    Queue
)

from customersSupportSystem import settings as helpdesk_settings


def huser_from_request(req):
    return HelpdeskUser(req.user)


class HelpdeskUser:
    def __init__(self, user):
        self.user = user

    def get_queues(self):
        all_queues = Queue.objects.all()

        return all_queues


    def get_tickets_in_queues(self):
        return Ticket.objects.filter(queue__in=self.get_queues())

    def has_full_access(self):
        return self.user.is_superuser or self.user.is_staff

    def can_access_queue(self, queue):

        if self.has_full_access():
            return True
        else:
            return self.user.has_perm(queue.permission_name)


    def can_access_ticket(self, ticket):
        user = self.user
        if self.can_access_queue(ticket.queue):
            return True
        elif self.has_full_access() or \
                (ticket.assigned_to and user.id == ticket.assigned_to.id):
            return True
        else:
            return False

