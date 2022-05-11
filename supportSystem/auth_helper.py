from urllib.parse import urlencode

import msal
from django.conf import settings
from django.contrib.auth.models import User
import os

AAD_TENANT_ID = os.getenv("AAD_TENANT_ID")
AAD_CLIENT_ID = os.getenv("AAD_CLIENT_ID")
AAD_AUTHORITY = os.getenv("AAD_AUTHORITY")
AAD_SECRET = os.getenv("AAD_SECRET")
AAD_SCOPE = getattr(settings, 'AAD_SCOPE')
REDIRECT_URL = os.getenv("REDIRECT_URL")


def load_cache(request):
    # Check for a token cache in the session
    cache = msal.SerializableTokenCache()
    if request.session.get('token_cache'):
        cache.deserialize(request.session['token_cache'])
    return cache


def save_cache(request, cache):
    # If cache has changed, persist back to session
    if cache.has_state_changed:
        request.session['token_cache'] = cache.serialize()


def get_msal_app(cache=None):
    # Initialize the MSAL confidential client
    auth_app = msal.ConfidentialClientApplication(
        AAD_CLIENT_ID,
        authority=AAD_AUTHORITY + AAD_TENANT_ID,
        client_credential=AAD_SECRET,
        token_cache=cache)
    print(auth_app)
    return auth_app


# Method to generate a sign-in flow
def get_sign_in_flow():
    auth_app = get_msal_app()
    return auth_app.initiate_auth_code_flow(
        AAD_SCOPE,
        redirect_uri=REDIRECT_URL)


# Method to exchange auth code for access token
def get_token_from_code(request):
    cache = load_cache(request)
    auth_app = get_msal_app(cache)

    # Get the flow saved in session
    flow = request.session.pop('auth_flow', {})
    result = auth_app.acquire_token_by_auth_code_flow(flow, request.GET)
    save_cache(request, cache)

    return result


def store_user(request, user):
    try:
        request.session['user'] = {
            'is_authenticated': True,
            'name': user['displayName'],
            'email': user['mail'] if (user['mail'] is not None) else user['userPrincipalName'],
            'timeZone': 'UTC'
        }
    except Exception as e:
        print(e)


def get_token(request):
    cache = load_cache(request)
    auth_app = get_msal_app(cache)

    accounts = auth_app.get_accounts()
    if accounts:
        result = auth_app.acquire_token_silent(
            AAD_SCOPE,
            account=accounts[0])
        save_cache(request, cache)

        return result['access_token']


def remove_user_and_token(request):
    if 'token_cache' in request.session:
        del request.session['token_cache']

    if 'user' in request.session:
        del request.session['user']


def get_mail_from_payload(user):
    if user.get('mail') is not None:
        email = user['mail'].lower()
    else:
        email = user['userPrincipalName'].lower()
    return email


def get_sys_users(user):
    print(user)
    email = get_mail_from_payload(user)

    print(email)
    sys_user = User.objects.filter(email=email)
    print(sys_user)
    return sys_user


def get_permissions(group, is_staff=False, is_superuser=False):
    print(str(group))
    if 'helpdesk_staff' in str(group):
        is_staff = True
    elif 'helpdesk_administrators' in str(group):
        is_superuser = True
    elif 'helpdesk_administrators' and 'helpdesk_staff' in str(group):
        is_superuser = True
        is_staff = True
    print(is_staff)
    return is_staff, is_superuser


def get_sys_user(user, group):
    users = get_sys_users(user)

    email = get_mail_from_payload(user)

    if len(users) == 0:
        is_staff, is_superuser = get_permissions(group)
        username = user['displayName']

        sys_user = User.objects.create_user(username=username, email=email, is_staff=is_staff, is_superuser=is_superuser)
        return sys_user
    elif len(users) == 1:
        sys_user = User.objects.get(email=email)
        return sys_user


def get_logout_url(redirect_uri, authority=AAD_AUTHORITY, tenant_id=AAD_TENANT_ID):
    params = urlencode({
        'post_logout_redirect_uri': redirect_uri,
    })
    return '{authority}/{tenant_id}/oauth2/logout?{params}'.format(
        authority=authority,
        tenant_id=tenant_id,
        params=params,
    )
