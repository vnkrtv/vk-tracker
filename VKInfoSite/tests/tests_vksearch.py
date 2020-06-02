# pylint: disable=invalid-name, unused-argument
"""
VK Search app tests, covered views.py, mongo.py and vk_scripts.py
"""
import json
from unittest import mock
from django.test import Client
from django.urls import reverse
from main import mongo
from vksearch.mongo import VKSearchFiltersStorage
from .tests_main import MainTest


class AddFilterTest(MainTest):
    """
    Tests for adding filter pages
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
        storage.delete_philter(filter_name=filter_name)


class DeleteFilterTest(MainTest):
    """
    Tests for deleting filter pages
    """

    def setUp(self) -> None:
        """
        Log in user and add search filter
        """
        super().setUp()
        self.client = Client()
        self.client.post(reverse('main:login_page'), {
            'username': self.user.username,
            'password': 'top_secret'
        }, follow=True)
        self.new_filter = {
            "cities": [1, 2, 99],
            "cities_titles": ["Москва", "Санкт-Петербург", "Новосибирск"],
            "country_id": 1,
            "friends": [789731504],
            "groups": [33098468],
            "name": "NewFilter",
            "universities": [2, 236, 242, 128]
        }
        self.storage = VKSearchFiltersStorage.connect(db=mongo.get_conn())
        self.storage.add_filter(new_filter=self.new_filter)

    def test_delete_filter_get_method(self):
        """
        Test for displaying 'delete_filter/' page
        """
        response = self.client.get(reverse('vksearch:delete_filter'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Delete filter')
        self.assertContains(response, 'Select filter to delete:')
        self.assertContains(response, self.new_filter['name'])

        self.storage.delete_philter(filter_name=self.new_filter['name'])

    def test_delete_filter_result(self) -> None:
        """
        Test for deleting search filter by web interface
        """

        filters = self.storage.get_all_philters_names()
        self.assertEqual(len(filters), 1)
        self.assertEqual(filters[0], self.new_filter['name'])

        response = self.client.post(reverse('vksearch:delete_filter_result'), {
            'filter': [self.new_filter['name']]
        }, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Deleting result')
        self.assertContains(response, self.new_filter['name'])
        self.assertContains(response, 'was successfully deleted.')

        filters = self.storage.get_all_philters_names()
        self.assertEqual(len(filters), 0)


class SearchTest(MainTest):
    """
    Tests for vk users searching pages
    """

    def setUp(self) -> None:
        """
        Log in user and add search filter
        """
        super().setUp()
        self.client = Client()
        self.client.post(reverse('main:login_page'), {
            'username': self.user.username,
            'password': 'top_secret'
        }, follow=True)
        self.new_filter = {
            "cities": [1, 2, 99],
            "cities_titles": ["Москва", "Санкт-Петербург", "Новосибирск"],
            "country_id": 1,
            "friends": [789731504],
            "groups": [33098468],
            "name": "NewFilter",
            "universities": [2, 236, 242, 128]
        }
        self.storage = VKSearchFiltersStorage.connect(db=mongo.get_conn())
        self.storage.add_filter(new_filter=self.new_filter)

    def test_search_get_method(self):
        """
        Test for displaying 'search/' page
        """
        response = self.client.get(reverse('vksearch:get_search_params'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Search')
        self.assertContains(response, 'Query string:')
        self.assertContains(response, self.new_filter['name'])

        self.storage.delete_philter(filter_name=self.new_filter['name'])

    @mock.patch('vksearch.views.vk_api')
    def test_search_results(self, vk_api) -> None:
        """
        Test for displaying result of searching
        """

        def vk_api_side_effect(request, method, **kwargs):
            if vk_api_side_effect.counter == 0:
                with open('VKInfoSite/tests/tests_data/search_by_groups_results.json', 'r') as f:
                    vk_response = json.load(f)
            else:
                with open('VKInfoSite/tests/tests_data/search_by_friends_results.json', 'r') as f:
                    vk_response = json.load(f)
            vk_api_side_effect.counter += 1
            return vk_response

        vk_api_side_effect.counter = 0

        vk_api.side_effect = vk_api_side_effect
        response = self.client.post(reverse('vksearch:get_search_result'), {
            'groups_selected': ['on'],
            'friends_selected': ['on'],
            'sex': ['0'],
            'q': ['Name'],
            'age_from': ['18'],
            'age_to': ['21'],
            'has_photo': ['on'],
            'filter': [self.new_filter['name']]
        }, follow=True)

        with open('VKInfoSite/tests/tests_data/search_by_groups_results.json', 'r') as file:
            response_by_groups = json.load(file)[0]['items']

        with open('VKInfoSite/tests/tests_data/search_by_friends_results.json', 'r') as file:
            response_by_friends = json.load(file)[0]['items']

        common_ids = {item['id'] for item in response_by_groups}
        common_ids &= {item['id'] for item in response_by_friends}

        unique_ids = {item['id'] for item in response_by_groups}
        unique_ids ^= {item['id'] for item in response_by_friends}

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Search result: found %d persons' % len(common_ids))

        for person_id in common_ids:
            self.assertContains(response, person_id)

        for person_id in unique_ids:
            self.assertNotContains(response, person_id)
