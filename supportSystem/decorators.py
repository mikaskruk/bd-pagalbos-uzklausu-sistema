from functools import wraps

from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.shortcuts import redirect

from django.contrib.auth.decorators import user_passes_test


from customersSupportSystem import settings as helpdesk_settings


def check_staff_status(check_staff=False):
    def check_superuser_status(check_superuser):
        def check_user_status(u):
            is_ok = u.is_authenticated and u.is_active
            if check_staff:
                return is_ok and u.is_staff
            elif check_superuser:
                return is_ok and u.is_superuser
            else:
                return is_ok
        return check_user_status
    return check_superuser_status


is_helpdesk_staff = check_staff_status(True)(False)

helpdesk_staff_member_required = user_passes_test(is_helpdesk_staff)
helpdesk_superuser_required = user_passes_test(check_staff_status(False)(True))


def protect_view(view_func):

    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('supportSystem:signin')
        elif not request.user.is_authenticated:
            raise Http404
        return view_func(request, *args, **kwargs)

    return _wrapped_view


def staff_member_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated and not request.user.is_active:
            return redirect('supportSystem:signin')
        if not  request.user.is_staff:
            raise PermissionDenied()
        return view_func(request, *args, **kwargs)

    return _wrapped_view


def superuser_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated and not request.user.is_active:
            return redirect('supportSystem:signin')
        if not request.user.is_superuser:
            raise PermissionDenied()
        return view_func(request, *args, **kwargs)

    return _wrapped_view
