# pylint: disable=import-error, invalid-name, too-few-public-methods, relative-beyond-top-level
"""
Main app tests, covered views.py, models.py, mongo.py, neo4j.py, vk_analytics.py and vk_models.py
"""
from django.test import TestCase, Client
from unittest import mock
from django.urls import reverse
from django.contrib.auth.models import User
from django.conf import settings
from .models import VKToken
from .vk_models import VKInfo
from .vk_analytics import VKAnalyzer, VKRelation
from . import mongo

FIRST_USER = {
    "domain": "id1234567",
    "followers": {
      "count": 1,
      "items": [
        {
          "id": 2776995,
          "first_name": "FollowerName",
          "last_name": "FollowerSurname",
          "sex": 2,
          "domain": "id2776777",
          "bdate": "19.6",
          "city": {
            "id": 1,
            "title": "Москва"
          }
        }
      ]
    },
    "friends": {
      "count": 2,
      "items": [
        {
          "id": 726666,
          "first_name": "FirstFriendName",
          "last_name": "FirstFriendSurname",
          "is_closed": True,
          "can_access_closed": False,
          "sex": 2,
          "domain": "friend1",
          "city": {
            "id": 1,
            "title": "Москва"
          },
          "country": {
            "id": 1,
            "title": "Россия"
          },
          "track_code": "708c102aX4WsYM3deGhjj7vgetw4_LUSeUySFcV-h90VzQU_9WI-5pRVnt19Z2OLvQC3USyLoWAQ"
        },
        {
          "id": 771335,
          "first_name": "SecondFriendName",
          "last_name": "SecondFriendSurname",
          "is_closed": False,
          "can_access_closed": True,
          "sex": 2,
          "domain": "friend2",
          "bdate": "16.1.1964",
          "city": {
            "id": 1,
            "title": "Москва"
          },
          "country": {
            "id": 1,
            "title": "Россия"
          },
          "home_phone": "",
          "track_code": "b4ff0437q6yrvkLit2d4VhBKKcfJrsS-Gu856RM6pJvV_GMBDL_Kz8jcTbOxbClTF6rkSt3Z0Mxz"
        }
      ]
    },
    "groups": {
      "count": 2,
      "items": [
        {
          "id": 29905644,
          "name": "First Group",
          "screen_name": "group1",
          "is_closed": 0,
          "type": "page",
          "is_admin": 0,
          "is_member": 0,
          "is_advertiser": 0
        },
        {
          "id": 183488077,
          "name": "Second Group",
          "screen_name": "group2",
          "is_closed": 0,
          "type": "page",
          "is_admin": 0,
          "is_member": 0,
          "is_advertiser": 0
        }
      ]
    },
    "id": 1234567,
    "main_info": {
      "id": 1234567,
      "first_name": "First",
      "last_name": "User",
      "is_closed": False,
      "can_access_closed": True,
      "sex": 2,
      "domain": "id1234567",
      "bdate": "22.3",
      "photo_id": "1432599_323470242",
      "mobile_phone": "",
      "home_phone": "",
      "site": "",
      "status": "",
      "verified": 0,
      "followers_count": 1,
      "counters": {
        "albums": 1,
        "videos": 14,
        "audios": 0,
        "photos": 2,
        "friends": 2,
        "mutual_friends": 0,
        "followers": 1,
        "subscriptions": 0,
        "pages": 2
      }
    },
    "photos": {
      "count": 2,
      "items": [
        {
          "photo_id": 323470247,
          "likes": {
            "count": 1,
            "items": [
              {
                "type": "profile",
                "id": 726666,
                "first_name": "FirstFriendName",
                "last_name": "FirstFriendSurname",
                "is_closed": False,
                "can_access_closed": True
              }
            ]
          },
          "comments": {
            "count": 0,
            "items": []
          }
        },
        {
          "photo_id": 288240728,
          "likes": {
            "count": 2,
            "items": [
              {
                "type": "profile",
                "id": 726666,
                "first_name": "FirstFriendName",
                "last_name": "FirstFriendSurname",
                "is_closed": False,
                "can_access_closed": True
              },
              {
                "type": "profile",
                "id": 771335,
                "first_name": "SecondFriendName",
                "last_name": "SecondFriendSurname",
                "is_closed": False,
                "can_access_closed": True
              }
            ]
          },
          "comments": {
            "count": 0,
            "items": []
          }
        }
      ]
    },
    "wall": {
      "count": 1,
      "items": [
        {
          "post_id": 179,
          "text": "",
          "likes": {
            "count": 0,
            "items": []
          },
          "comments": {
            "count": 0,
            "items": []
          }
        }
      ]
    }
}

SECOND_USER = {
    "domain": "id1234567",
    "followers": {
      "count": 1,
      "items": [
        {
          "id": 2776995,
          "first_name": "FollowerName",
          "last_name": "FollowerSurname",
          "sex": 2,
          "domain": "id2776777",
          "bdate": "19.6",
          "city": {
            "id": 1,
            "title": "Москва"
          }
        }
      ]
    },
    "friends": {
      "count": 1,
      "items": [
        {
          "id": 1234567,
          "first_name": "First",
          "last_name": "User",
          "is_closed": True,
          "can_access_closed": False,
          "sex": 2,
          "domain": "id1234567",
          "city": {
            "id": 1,
            "title": "Москва"
          },
          "country": {
            "id": 1,
            "title": "Россия"
          },
          "track_code": "708c102aX4WsYM3deGhjj7vgetw4_LUSeUySFcV-h90VzQU_9WI-5pRVnt19Z2OLvQC3USyLoWAQ"
        }
      ]
    },
    "groups": {
      "count": 1,
      "items": [
        {
          "id": 183488077,
          "name": "Second Group",
          "screen_name": "group2",
          "is_closed": 0,
          "type": "page",
          "is_admin": 0,
          "is_member": 0,
          "is_advertiser": 0
        }
      ]
    },
    "id": 726666,
    "main_info": {
      "id": 726666,
      "first_name": "FirstFriendName",
      "last_name": "FirstFriendSurname",
      "is_closed": False,
      "can_access_closed": True,
      "sex": 2,
      "domain": "friend1",
      "bdate": "22.3",
      "photo_id": "1432509_323470242",
      "mobile_phone": "",
      "home_phone": "",
      "site": "",
      "status": "",
      "verified": 0,
      "followers_count": 1,
      "counters": {
        "albums": 1,
        "videos": 14,
        "audios": 0,
        "photos": 0,
        "friends": 1,
        "mutual_friends": 0,
        "followers": 1,
        "subscriptions": 0,
        "pages": 1
      }
    },
    "photos": {
      "count": 0,
      "items": []
    },
    "wall": {
      "count": 1,
      "items": []
    }
}


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


class AddUserTest(MainTest):
    """
    Tests for 'add_user' and 'add_user_result' pages
    """

    def setUp(self) -> None:
        super().setUp()
        self.client = Client()
        self.client.post(reverse('main:login_page'), {
            'username': self.user.username,
            'password': 'top_secret'
        }, follow=True)

    def test_add_user_get_method(self) -> None:
        response = self.client.get(reverse('main:add_user'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Add user')
        self.assertContains(response, 'Enter user domain:')

    @mock.patch('main.vk_models.VKUser.open_session', return_value=None)
    @mock.patch('main.vk_models.VKInfo.get_main_info', return_value=FIRST_USER['main_info'])
    @mock.patch('main.vk_models.VKInfo.get_friends', return_value=FIRST_USER['friends'])
    @mock.patch('main.vk_models.VKInfo.get_followers', return_value=FIRST_USER['followers'])
    @mock.patch('main.vk_models.VKInfo.get_photos', return_value=FIRST_USER['photos'])
    @mock.patch('main.vk_models.VKInfo.get_wall', return_value=FIRST_USER['wall'])
    @mock.patch('main.vk_models.VKInfo.get_groups', return_value=FIRST_USER['groups'])
    def test_add_user_result(self, *args) -> None:
        """
        Test for adding user by web interface
        """
        response = self.client.post(reverse('main:add_user_result'), {
            'domain': FIRST_USER['main_info']['domain']
        }, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Add result')
        self.assertContains(response, 'First User')
        self.assertContains(response, 'was successfully added to databases!')
