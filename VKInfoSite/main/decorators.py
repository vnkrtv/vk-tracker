# pylint: disable=import-error, no-else-return
"""
Decorators for differentiate user rights
"""
from django.http import HttpResponse
from django.shortcuts import redirect, render
from vk.exceptions import VkAPIError


def unauthenticated_user(view_func):
    """
    Checked if user is authorized
    """
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_authenticated:
            return view_func(request, *args, **kwargs)
        else:
            return redirect('/')
    return wrapper_func


def check_token(view_func):
    """
    Checked if vk token is valid
    """
    def wrapper_func(request, *args, **kwargs):
        try:
            return view_func(request, *args, **kwargs)
        except VkAPIError as e:
            info = {
                'title': 'Error | VK Tracker',
                'message_title': 'Error',
                'message': str(e).split('. ')[1] + '.'
            }
            return render(request, 'info.html', info)
    return wrapper_func


def allowed_users(allowed_roles: list):
    """
    Checked if user belong to allowed group

    :param allowed_roles: 'student' or 'lecturer'
    """
    def decorator(view_func):
        def wrapper_func(request, *args, **kwargs):

            is_allowed = False
            for group in allowed_roles:
                if request.user.groups.filter(name=group):
                    is_allowed = True

            if is_allowed:
                return view_func(request, *args, **kwargs)
            else:
                return HttpResponse('You are not permitted to see this page.')
        return wrapper_func
    return decorator


def post_method(view_func):
    """
    Redirect to '/tests' page if method is not 'post'
    """
    def wrapper_func(request, *args, **kwargs):
        if request.method != 'POST':
            return redirect('/add_user')
        else:
            return view_func(request, *args, **kwargs)
    return wrapper_func
