import logging
from django.template import Library

from supportSystem.decorators import is_helpdesk_staff


logger = logging.getLogger(__name__)
register = Library()


@register.filter(name='is_helpdesk_staff')
def helpdesk_staff(user):
    try:
        return is_helpdesk_staff(user)
    except Exception:
        logger.exception("'helpdesk_staff' template tag (django-supportSystem) crashed")
