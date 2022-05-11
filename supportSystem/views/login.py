from django.contrib.auth import login
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from ..auth_helper import get_sign_in_flow, get_token_from_code, store_user, remove_user_and_token, get_token, \
    get_sys_user, get_logout_url
from ..graph_helper import *
from django.contrib.auth import logout


def home(request):
    context = initialize_context(request)
    return HttpResponseRedirect(reverse('supportSystem:home'), context)


def initialize_context(request):
    context = {}
    error = request.session.pop('flash_error', None)
    if error != None:
        context['errors'] = []
        context['errors'].append(error)
    # Check for user in the session
    context['user'] = request.session.get('user', {'is_authenticated': False})
    return context


def loginPage(request):
    if request.method == 'POST':
        return HttpResponseRedirect(reverse('supportSystem:signin'))
    return render(request, 'supportSystem/login.html')


def auth(request):
    # Get the sign-in flow
    flow = get_sign_in_flow()
    # Save flow
    try:
        request.session['auth_flow'] = flow
    except Exception as e:
        print(e)
    # Redirect to the Azure
    return HttpResponseRedirect(flow['auth_uri'])


def signout(request):
    logout(request)
    redirect = request.build_absolute_uri(reverse('supportSystem:home'))
    logout_url = get_logout_url(redirect)
    return HttpResponseRedirect(logout_url)


def callback(request):
    result = get_token_from_code(request)
    user = get_user(result['access_token'])
    group = get_group(result['access_token'])
    if user and group:
        store_user(request, user)
        sys_user = get_sys_user(user, group)
        login(user=sys_user, request=request)
        return HttpResponseRedirect(reverse('supportSystem:dashboard'))
    else:
        return HttpResponseRedirect(reverse('supportSystem:login'))




