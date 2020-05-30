# pylint: disable=import-error, invalid-name, too-few-public-methods, relative-beyond-top-level
"""
Main app tests, covered views.py, models.py, mongo.py, neo4j.py, vk_analytics.py and vk_models.py
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.conf import settings
from .models import VKToken
from .vk_models import VKInfo
from .vk_analytics import VKAnalyzer, VKRelation
from . import mongo


class MainTest(TestCase):
    """
    Base class for all tests
    """

    def setUp(self) -> None:
        """
        Add objects to temporary test database:
        - groups 'lecturer' and 'student'
        - 'lecturer' user and 'student' user
        - study subject 'Subject'
        - Subject 'Subject' test 'Hard test'
        - 2 questions for 'Hard test'
        """
        self.user = User.objects.create_user(
            username='user',
            password='top_secret')

        mongo.set_conn(
            host=settings.DATABASES['default']['HOST'],
            port=settings.DATABASES['default']['PORT'],
            db_name=settings.DATABASES['default']['TEST']['NAME'])


class AuthorizationTest(MainTest):
    """
    Tests for authorization in the application
    """

    def test_successful_auth(self) -> None:
        """
        Test for successful authorization of users
        """
        client = Client()
        response = client.post(reverse('main:login_page'), {
            'username': self.user.username,
            'password': 'top_secret'
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Logout')

    def test_unsuccessful_auth(self) -> None:
        """
        Test for unsuccessful authorization of users
        """
        client = Client()
        response = client.post(reverse('main:login_page'), {
            'username': self.user.username,
            'password': 'wrong_password'
        }, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'username and password are incorrect.')


class RedirectTest(MainTest):
    """
    Tests for redirection in the application
    """

    def test_redirect(self) -> None:
        """
        Test redirection of unauthenticated users
        """
        client = Client()
        response = client.post(reverse('main:add_user'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Login page')
