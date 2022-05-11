import warnings
from pathlib import Path
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
import os
from django.utils.translation import gettext_lazy as _

DEFAULT_USER_SETTINGS = {
    'login_view_ticketlist': True,
    'email_on_ticket_change': True,
    'email_on_ticket_assign': True,
    'tickets_per_page': 25,
    'use_email_as_submitter': True,
}

BASE_DIR = Path(__file__).resolve().parent.parent


DEBUG = True

ALLOWED_HOSTS = ['support.mdesk.lt', 'https://suppaccountstorage.blob.core.windows.net']
CORS_ORIGIN_ALLOW_ALL = False

CORS_ORIGIN_WHITELIST = (
    'https://support.mdesk.lt',
    'https://suppaccountstorage.blob.core.windows.net',
)

CSRF_TRUSTED_ORIGINS = ['https://support.mdesk.lt']

INSTALLED_APPS = [
    'corsheaders',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'django.contrib.humanize',
    'bootstrap4form',
    'supportSystem',
    'storages',
]
SITE_ID = 1

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'customersSupportSystem.wsgi.application'

HELPDESK_PUBLIC_TICKET_QUEUE = 'public'

if os.getenv("DATABASE_NAME") is None:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': 'mydatabase',
        }
    }
else:

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            'NAME': os.getenv('DATABASE_NAME'),
            'USER': os.getenv('DATABASE_USER'),
            'PASSWORD': os.getenv('DATABASE_PASSWORD'),
            'HOST': os.getenv('DATABASE_HOST'),
            'PORT': '5432',
            'OPTIONS': {'sslmode': 'require'}
        }
    }

STATIC_LOCATION = "static"
MEDIA_LOCATION = "media"


HELPDESK_EMAIL_SUBJECT_TEMPLATE = getattr(
    settings, 'HELPDESK_EMAIL_SUBJECT_TEMPLATE',
    "{{ ticket.ticket }} {{ ticket.title|safe }} %(subject)s")
# since django-supportSystem may not work correctly without the ticket ID
# in the subject, let's do a check for it quick:
if HELPDESK_EMAIL_SUBJECT_TEMPLATE.find("ticket.ticket") < 0:
    raise ImproperlyConfigured

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_USE_TLS = True
EMAIL_HOST = os.getenv("EMAIL_HOST")
EMAIL_PORT = 587
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')

DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL')



HELPDESK_MAX_EMAIL_ATTACHMENT_SIZE = '512000'

LANGUAGE_CODE = 'lt'

LANGUAGES = (
    ('lt', _('Lithuanian')),
    ('en', _('English')),
)

LOCALE_PATHS = (
    os.path.join(BASE_DIR, 'locale/'),
)

CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'None'
SESSION_COOKIE_SECURE = True