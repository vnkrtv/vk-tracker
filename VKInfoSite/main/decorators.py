"""Custom decorators"""
import requests
from django.shortcuts import redirect, render
from vk.exceptions import VkAPIError, VkException


def unauthenticated_user(view_func):
    """Checked if user is authorized"""
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_authenticated:
            return view_func(request, *args, **kwargs)
        return redirect('/')
    return wrapper_func


def check_token(view_func):
    """Checked if vk token is valid"""
    def wrapper_func(request, *args, **kwargs):
        try:
            return view_func(request, *args, **kwargs)
        except VkAPIError as error:
            context = {
                'title': 'Error | VK Tracker',
                'message_title': 'Error',
                'message': str(error).split('. ')[1] + '.'
            }
            return render(request, 'info.html', context)
        except VkException as vk_error:
            context = {
                'title': 'Error | VK Tracker',
                'message_title': 'Error',
                'message': vk_error
            }
            return render(request, 'info.html', context)
        except requests.exceptions.ConnectionError:
            context = {
                'title': 'Error | VK Tracker',
                'message_title': 'Error',
                'message': 'No connection to the internet.'
            }
            return render(request, 'info.html', context)
    return wrapper_func


def post_method(view_func):
    """Redirect to '/tests' page if method is not 'post'"""
    def wrapper_func(request, *args, **kwargs):
        if request.method != 'POST':
            return redirect('/add_user')
        return view_func(request, *args, **kwargs)
    return wrapper_func
