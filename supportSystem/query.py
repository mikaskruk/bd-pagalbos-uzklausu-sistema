from django.db.models import Q
from django.urls import reverse
from django.utils.html import escape
from django.utils.translation import gettext_lazy as _

from base64 import b64encode
from base64 import b64decode
import json

from model_utils import Choices

from supportSystem.serializers import DatatablesTicketSerializer


def query_to_base64(query):
    return b64encode(json.dumps(query).encode('UTF-8')).decode("ascii")


def query_from_base64(b64data):
    query = {'search_string': ''}
    query.update(json.loads(b64decode(b64data).decode('utf-8')))
    if query['search_string'] is None:
        query['search_string'] = ''
    return query


def query_to_dict(results, descriptions):
    output = []
    for data in results:
        row = {}
        i = 0
        for column in descriptions:
            row[column[0]] = data[i]
            i += 1

        output.append(row)
    return output


def get_search_filter_args(search):
    if search.startswith('queue:'):
        return Q(queue__title__icontains=search[len('queue:'):])
    if search.startswith('priority:'):
        return Q(priority__icontains=search[len('priority:'):])
    filter = Q()
    for subsearch in search.split("OR"):
        subsearch = subsearch.strip()
        filter = (
            filter |
            Q(id__icontains=subsearch) |
            Q(title__icontains=subsearch) |
            Q(description__icontains=subsearch) |
            Q(priority__icontains=subsearch) |
            Q(resolution__icontains=subsearch) |
            Q(submitter_email__icontains=subsearch) |
            Q(assigned_to__email__icontains=subsearch) |
            Q(ticketcustomfieldvalue__value__icontains=subsearch) |
            Q(created__icontains=subsearch) |
            Q(due_date__icontains=subsearch)
        )
    return filter


DATATABLES_ORDER_COLUMN_CHOICES = Choices(
    ('0', 'id'),
    ('1', 'title'),
    ('2', 'priority'),
    ('3', 'queue'),
    ('4', 'status'),
    ('5', 'created'),
    ('6', 'due_date'),
    ('7', 'assigned_to'),
    ('8', 'submitter_email'),
)


def get_query_class():
    from django.conf import settings

    def _get_query_class():
        return __Query__
    return getattr(settings,
                   'HELPDESK_QUERY_CLASS',
                   _get_query_class)()


class __Query__:
    def __init__(self, huser, base64query=None, query_params=None):
        self.huser = huser
        self.params = query_params if query_params else query_from_base64(base64query)
        self.base64 = base64query if base64query else query_to_base64(query_params)
        self.result = None

    def get_search_filter_args(self):
        search = self.params.get('search_string', '')
        return get_search_filter_args(search)

    def __run__(self, queryset):
        filter = self.params.get('filtering', {})
        filter_or = self.params.get('filtering_or', {})
        queryset = queryset.filter((Q(**filter) | Q(**filter_or)) & self.get_search_filter_args())
        sorting = self.params.get('sorting', None)
        if sorting:
            sortreverse = self.params.get('sortreverse', None)
            if sortreverse:
                sorting = "-%s" % sorting
            queryset = queryset.order_by(sorting)
        return queryset.distinct()

    def get(self):
        tickets = self.huser.get_tickets_in_queues().select_related()
        return self.__run__(tickets)

    def get_datatables_context(self, **kwargs):
        objects = self.get()
        order_by = '-created'
        draw = int(kwargs.get('draw', [0])[0])
        length = int(kwargs.get('length', [25])[0])
        start = int(kwargs.get('start', [0])[0])
        search_value = kwargs.get('search[value]', [""])[0]
        order_column = kwargs.get('order[0][column]', ['5'])[0]
        order = kwargs.get('order[0][dir]', ["asc"])[0]

        order_column = DATATABLES_ORDER_COLUMN_CHOICES[order_column]

        if order == 'desc':
            order_column = '-' + order_column

        queryset = objects.all().order_by(order_by)
        total = queryset.count()

        if search_value:
            queryset = queryset.filter(get_search_filter_args(search_value))

        count = queryset.count()
        queryset = queryset.order_by(order_column)[start:start + length]
        return {
            'data': DatatablesTicketSerializer(queryset, many=True).data,
            'recordsFiltered': count,
            'recordsTotal': total,
            'draw': draw
        }

    def get_timeline_context(self):
        events = []

        for ticket in self.get():
            for followup in ticket.followup_set.all():
                event = {
                    'start_date': self.mk_timeline_date(followup.date),
                    'text': {
                        'headline': ticket.title + ' - ' + followup.title,
                        'text': (
                            (escape(followup.comment) if followup.comment else _('No text'))
                            +
                            '<br/> <a href="%s" class="btn" role="button">%s</a>'
                            %
                            (reverse('supportSystem:view', kwargs={'ticket_id': ticket.pk}), _("View ticket"))
                        ),
                    },
                    'group': _('Messages'),
                }
                events.append(event)

        return {
            'events': events,
        }

    def mk_timeline_date(self, date):
        return {
            'year': date.year,
            'month': date.month,
            'day': date.day,
            'hour': date.hour,
            'minute': date.minute,
            'second': date.second,
        }
