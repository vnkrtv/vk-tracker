# pylint: disable=import-error, no-else-return
"""
Custom decorators
"""
from django.shortcuts import redirect, render
from vk.exceptions import VkAPIError, VkException


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
            context = {
                'title': 'Error | VK Tracker',
                'message_title': 'Error',
                'message': str(e).split('. ')[1] + '.'
            }
            return render(request, 'info.html', context)
        except VkException as e:
            context = {
                'title': 'Error | VK Tracker',
                'message_title': 'Error',
                'message': e
            }
            return render(request, 'info.html', context)

    return wrapper_func


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
