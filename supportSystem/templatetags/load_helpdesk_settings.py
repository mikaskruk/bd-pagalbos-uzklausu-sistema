from django.template import Library
from customersSupportSystem import settings as helpdesk_settings_config

def load_helpdesk_settings(request):
    try:
        return helpdesk_settings_config
    except Exception as e:
        import sys
        print("'load_helpdesk_settings' template tag (django-supportSystem) crashed with following error:",
              file=sys.stderr)
        print(e, file=sys.stderr)
        return ''


register = Library()
register.filter('load_helpdesk_settings', load_helpdesk_settings)
