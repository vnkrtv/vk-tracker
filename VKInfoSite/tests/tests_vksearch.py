# pylint: disable=invalid-name
"""
VK Search app tests, covered views.py, mongo.py and vk_scripts.py
"""
import json
from unittest import mock
from django.test import Client
from django.urls import reverse
from main import mongo
from main.models import VKToken
from vksearch.mongo import VKSearchFiltersStorage
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
        VKToken.objects.create(
            user=self.user,
            token='vk_token')

    @mock.patch('vksearch.views.vk_api')
    def test_add_filter_1_get_method(self, vk_api):
        """
        Test for displaying 'add_filter/1/' page
        """
        countries = {
            'count': 2,
            'items': [
                {
                    'id': 1,
                    'title': 'Country_1'
                },
                {
                    'id': 2,
                    'title': 'Country_2'
                }
            ]
        }
        vk_api.return_value = countries

        response = self.client.get(reverse('vksearch:add_search_filter_1'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Add new filter (1/2)')
        self.assertContains(response, 'Country')
        self.assertContains(response, 'Cities')
        self.assertContains(response, 'Universities parameters')
        for country in countries['items']:
            self.assertContains(response, country['title'])

    @mock.patch('vksearch.views.vk_api')
    def test_add_search_filter_2(self, vk_api) -> None:
        """
        Test for displaying 'add_filter/2/' page
        """
        def vk_api_side_effect(request, method, **kwargs):
            vk_response = {}
            if method == 'database.getCities':
                vk_response = {
                    'count': 1,
                    'items': [
                        {
                            'id': 1,
                            'title': 'City_1'
                        }
                    ]
                }
            if method == 'database.getCountriesById':
                vk_response = {
                    'count': 2,
                    'items': [
                        {
                            'id': 1,
                            'title': 'Country_1'
                        }
                    ]
                }
            if method == 'execute':
                vk_response = [{
                    'count': 1,
                    'items': [
                        {
                            'id': 1,
                            'title': 'MSU'
                        }
                    ]
                }]
            return vk_response

        vk_api.side_effect = vk_api_side_effect
        response = self.client.post(reverse('vksearch:add_search_filter_2'), {
            'country_id': ['1'],
            'city_1': ['City_1'],
            'un_city_1': ['City_1'],
            'universities_filter': ['MSU']
        }, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Add new filter (2/2)')
        self.assertContains(response, 'MSU')
        self.assertContains(response, 'Filter name')
        self.assertContains(response, 'Universities')
        self.assertContains(response, 'Friends')
        self.assertContains(response, 'Groups')

    @mock.patch('vksearch.views.vk_api')
    def test_get_changes(self, vk_api) -> None:
        """
        Test for adding search filter by web interface
        """
        def vk_api_side_effect(request, method, **kwargs):
            vk_response = {}
            if method == 'users.get':
                vk_response = [{
                    'id': 1234567,
                    'domain': 'friend_domain',
                    'is_closed': False
                }]
            if method == 'groups.getById':
                vk_response = [{
                    'id': 7654321,
                    'domain': 'group_domain'
                }]
            return vk_response

        vk_api.side_effect = vk_api_side_effect

        filter_name = 'New search filter'
        cities_ids = [1, 2, 3]
        country_id = 5
        cities_titles = ["City_1", "City_2", "City_3"]
        university_id = 16

        storage = VKSearchFiltersStorage.connect(db=mongo.get_conn())
        self.assertEqual(storage.get_filter(filter_name=filter_name), {})

        response = self.client.post(reverse('vksearch:add_filter_result'), {
            'country_id': [str(country_id)],
            'cities_ids': [str(cities_ids)],
            'cities_titles': [cities_titles],
            'university_1': [str(university_id)],
            'filter_name': [filter_name],
            'friend_1': ['friend_domain'],
            'group_1': ['group_domain']
        }, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Adding result')
        self.assertContains(response, filter_name)
        self.assertContains(response, ' was successfully added to base.')

        added_filter = storage.get_filter(filter_name=filter_name)
        added_filter.pop('_id')
        predicted_filter = {
            'name': filter_name,
            'country_id': country_id,
            'cities': cities_ids,
            'cities_titles': str(cities_titles),
            'universities': [university_id],
            'friends': [1234567],
            'groups': [7654321]
        }
        self.assertEqual(added_filter, predicted_filter)
