# pylint: disable=invalid-name
"""
VK Search app tests, covered views.py, mongo.py and vk_scripts.py
"""
import json
from datetime import datetime
from unittest import mock
from unittest import skip
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.conf import settings
from bson import ObjectId
from main import mongo
from .tests_main import MainTest


class AddFilterTest(MainTest):

    """
    Test for add filter pages
    """

    def setUp(self) -> None:
        """
        Log in user
        """
        super().setUp()
        self.client = Client()
        self.client.post(reverse('main:login_page'), {
            'username': self.user.username,
            'password': 'top_secret'
        }, follow=True)

    @skip
    @mock.patch('vksearch.vk_scripts.vk_api')
    def test_add_filter_1_get_method(self, vk_api):
        """
        Test for displaying 'add_filter/1/' page
        """
        countries = [{'id': 1, 'title': 'Country_1'}, {'id': 2, 'title': 'Country_2'}]
        vk_api.return_value = countries
        response = self.client.get(reverse('vksearch:add_search_filter_1'), follow=True)
        self.assertEqual(response.status_code, 200)
        print(response.content)
        self.assertContains(response, 'Add new filter (1/2)')
        self.assertContains(response, 'Country')
        self.assertContains(response, 'Cities')
        self.assertContains(response, 'Universities parameters')
        for country in countries:
            self.assertContains(response, country['title'])

    @skip
    def test_get_changes_dates(self) -> None:
        """
        Test for getting dates user info was collected by web interface
        """
        domain = self.first_user['main_info']['domain']
        response = self.client.post(reverse('main:get_dates'), {
            'domain': domain
        }, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Get dates')
        self.assertContains(response, self.first_user['date'])
        self.assertContains(response, self.changed_first_user['date'])

    @skip
    def test_get_changes(self) -> None:
        """
        Test for getting user account info changes by web interface
        """
        domain = self.first_user['main_info']['domain']
        response = self.client.post(reverse('main:get_user_changes'), {
            'domain': domain,
            'date1': self.first_user['date'],
            'date2': self.changed_first_user['date']
        }, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'First User')
        self.assertContains(response, 'account changes')

        deleted_friend = self.first_user['friends']['items'][1]
        deleted_follower = self.first_user['followers']['items'][0]
        deleted_group = self.first_user['groups']['items'][1]
        deleted_photo = self.first_user['photos']['items'][1]
        new_like = '<a href="https://vk.com/id771335">SecondFriendName SecondFriendSurname</a>[NEW]'

        self.assertContains(response, deleted_friend['id'])
        self.assertContains(response, deleted_follower['id'])
        self.assertContains(response, deleted_group['id'])
        self.assertContains(response, deleted_photo['photo_id'])
        self.assertContains(response, new_like)
