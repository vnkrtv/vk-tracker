# pylint: disable=invalid-name, too-many-arguments
"""
Main app tests, covered views.py, models.py, mongo.py, neo4j.py, vk_analytics.py and vk_models.py
"""
import json
from datetime import datetime
from unittest import mock
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.conf import settings
from bson import ObjectId
from main import mongo


class MainTest(TestCase):
    """
    Base class for all tests
    """

    def setUp(self) -> None:
        """
        Add user to temporary test database and
        set connection for custom classes
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

    def test_redirect_unauthenticated_users(self) -> None:
        """
        Test redirection of unauthenticated users
        """
        client = Client()
        response = client.post(reverse('main:add_user'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Login page')

    def test_redirect_get_methods(self) -> None:
        """
        Test redirection to 'add_user/' page if method is not post
        """
        client = Client()
        client.post(reverse('main:login_page'), {
            'username': self.user.username,
            'password': 'top_secret'
        }, follow=True)

        response = client.get(reverse('main:add_user_result'))
        self.assertEqual(response.status_code, 302)

        response = client.get(reverse('main:get_user_changes'))
        self.assertEqual(response.status_code, 302)

        response = client.get(reverse('main:get_relations'))
        self.assertEqual(response.status_code, 302)


class AuthorizedMainTest(MainTest):
    """
    Base class for testing auth user requests
    """

    def setUp(self) -> None:
        """
        Log in user and load 3 json files with test users information
        """
        super().setUp()
        self.client = Client()
        self.client.post(reverse('main:login_page'), {
            'username': self.user.username,
            'password': 'top_secret'
        }, follow=True)

        with open('VKInfoSite/tests/test_data/first_user.json', 'r') as file:
            self.first_user = json.load(file)

        with open('VKInfoSite/tests/test_data/changed_first_user.json', 'r') as file:
            self.changed_first_user = json.load(file)

        with open('VKInfoSite/tests/test_data/second_user.json', 'r') as file:
            self.second_user = json.load(file)


class AddUserTest(AuthorizedMainTest):
    """
    Tests for 'add_user' and 'add_user_result' pages
    """

    def test_add_user_get_method(self) -> None:
        """
        Test for displaying 'add_user/' page
        """
        response = self.client.get(reverse('main:add_user'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Add user')
        self.assertContains(response, 'Enter user domain:')

    @mock.patch('main.vk_api.VKUser.open_session')
    @mock.patch('main.vk_api.VKInfo.get_main_info')
    @mock.patch('main.vk_api.VKInfo.get_friends')
    @mock.patch('main.vk_api.VKInfo.get_followers')
    @mock.patch('main.vk_api.VKInfo.get_photos')
    @mock.patch('main.vk_api.VKInfo.get_wall')
    @mock.patch('main.vk_api.VKInfo.get_groups')
    def test_add_user_result(self, get_groups, get_wall, get_photos,
                             get_followers, get_friends, get_main_info, open_session) -> None:
        """
        Test for adding user by web interface
        """
        open_session.return_value = None
        get_main_info.return_value = self.first_user['main_info']
        get_friends.return_value = self.first_user['friends']
        get_followers.return_value = self.first_user['followers']
        get_photos.return_value = self.first_user['photos']
        get_wall.return_value = self.first_user['wall']
        get_groups.return_value = self.first_user['groups']

        domain = self.first_user['main_info']['domain']

        storage = mongo.VKInfoStorage.connect(db=mongo.get_conn())
        user_info = storage.get_user(domain=domain)
        self.assertEqual(user_info, {})

        response = self.client.post(reverse('main:add_user_result'), {
            'domain': domain
        }, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Add result')
        self.assertContains(response, 'First User')
        self.assertContains(response, 'was successfully added to databases!')

        user_info = storage.get_user(domain=domain)
        user_info.pop('_id')
        user_info.pop('date')
        self.maxDiff = None
        self.assertEqual(user_info, self.first_user)


class UserInfoTest(AuthorizedMainTest):
    """
    Test for users info pages
    """

    def setUp(self) -> None:
        """
        Add first_user to temporary DB
        """
        super().setUp()
        date = datetime.now().timetuple()
        self.first_user['date'] = {
            'year': date[0],
            'month': date[1],
            'day': date[2],
            'hour': date[3],
            'minutes': date[4]
        }
        self.first_user['_id'] = str(ObjectId())
        storage = mongo.VKInfoStorage.connect(db=mongo.get_conn())
        storage.add_user(user=self.first_user)

    def test_user_info_get_method(self):
        """
        Test for displaying 'user_info/' page
        """
        response = self.client.get(reverse('main:user_info'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Get info')
        self.assertContains(response, 'Enter user domain:')

    def test_get_user_info(self) -> None:
        """
        Test for adding user by web interface
        """
        domain = self.first_user['main_info']['domain']
        response = self.client.post(reverse('main:get_user_info'), {
            'domain': domain
        }, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Information about')
        self.assertContains(response, 'First User')

        for friend in self.first_user['friends']['items']:
            self.assertContains(response, friend['id'])
        for follower in self.first_user['followers']['items']:
            self.assertContains(response, follower['id'])
        for group in self.first_user['groups']['items']:
            self.assertContains(response, group['id'])
        for post in self.first_user['wall']['items']:
            self.assertContains(response, post['post_id'])
        for photo in self.first_user['photos']['items']:
            self.assertContains(response, photo['photo_id'])


class UserChangesTest(AuthorizedMainTest):
    """
    Test for users changes info pages
    """

    def setUp(self) -> None:
        """
        Add normal and changed info about first_user to temporary DB
        """
        super().setUp()
        date = datetime.now().timetuple()

        self.first_user['date'] = {
            'year': date[0],
            'month': date[1],
            'day': date[2],
            'hour': date[3],
            'minutes': date[4]
        }
        self.first_user['_id'] = str(ObjectId())

        self.changed_first_user['date'] = {
            'year': date[0],
            'month': date[1],
            'day': date[2],
            'hour': date[3],
            'minutes': date[4] + 1
        }
        self.changed_first_user['_id'] = str(ObjectId())

        storage = mongo.VKInfoStorage.connect(db=mongo.get_conn())
        storage.add_user(user=self.first_user)
        storage.add_user(user=self.changed_first_user)

    def test_get_changes_get_method(self):
        """
        Test for displaying 'get_changes/' page
        """
        response = self.client.get(reverse('main:get_changes'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Get changes')
        self.assertContains(response, 'Enter user domain:')

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


class UsersRelationTest(AuthorizedMainTest):
    """
    Tests fo users relation info pages
    """

    def setUp(self) -> None:
        """
        Add first_user and second_user info to temporary DB
        """
        super().setUp()
        date = datetime.now().timetuple()

        self.first_user['date'] = {
            'year': date[0],
            'month': date[1],
            'day': date[2],
            'hour': date[3],
            'minutes': date[4]
        }
        self.first_user['_id'] = str(ObjectId())

        self.second_user['date'] = {
            'year': date[0],
            'month': date[1],
            'day': date[2],
            'hour': date[3],
            'minutes': date[4] + 1
        }
        self.second_user['_id'] = str(ObjectId())

        storage = mongo.VKInfoStorage.connect(db=mongo.get_conn())
        storage.add_user(user=self.first_user)
        storage.add_user(user=self.second_user)

    def test_get_relation_get_method(self):
        """
        Test for displaying 'mutual_activity/' page
        """
        response = self.client.get(reverse('main:get_mutual_activity'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Get users domains')
        self.assertContains(response, 'Enter first user domain:')
        self.assertContains(response, 'Enter second user domain:')

    def test_get_changes_dates(self) -> None:
        """
        Test for getting dates users info was collected
        """
        response = self.client.post(reverse('main:get_users_dates'), {
            'first_domain': self.first_user['main_info']['domain'],
            'second_domain': self.second_user['main_info']['domain']
        }, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Get dates')
        self.assertContains(response, 'First User')
        self.assertContains(response, 'FirstFriendName FirstFriendSurname')
        self.assertContains(response, self.first_user['date'])
        self.assertContains(response, self.second_user['date'])

    def test_get_changes(self) -> None:
        """
        Test for getting users mutual activity by web interface
        """
        response = self.client.post(reverse('main:get_relations'), {
            'first_domain': self.first_user['main_info']['domain'],
            'second_domain': self.second_user['main_info']['domain'],
            'date1': self.first_user['date'],
            'date2': self.second_user['date']
        }, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Mutual activity')
        self.assertContains(response, self.first_user['main_info']['domain'])
        self.assertContains(response, self.second_user['main_info']['domain'])

        mutual_friend = self.first_user['friends']['items'][1]
        mutual_group = self.first_user['groups']['items'][1]
        post_liked_by_second_user = self.first_user['wall']['items'][0]
        photos_liked_by_second_user = self.first_user['photos']['items']

        self.assertContains(response, mutual_friend['id'])
        self.assertContains(response, mutual_group['id'])
        self.assertContains(response, post_liked_by_second_user['post_id'])
        for photo in photos_liked_by_second_user:
            self.assertContains(response, photo['photo_id'])
