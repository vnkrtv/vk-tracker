# pylint: disable=import-error, invalid-name, too-few-public-methods, relative-beyond-top-level
"""
Main app tests, covered views.py, models.py, mongo.py, neo4j.py, vk_analytics.py and vk_models.py
"""
from django.test import TestCase, Client
from unittest import mock
from bson import ObjectId
from datetime import datetime
from django.urls import reverse
from django.contrib.auth.models import User
from django.conf import settings
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

CHANGED_FIRST_USER = {
    "domain": "id1234567",
    "followers": {
      "count": 0,
      "items": []
    },
    "friends": {
      "count": 1,
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
        }
      ]
    },
    "groups": {
      "count": 1,
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
      "followers_count": 0,
      "counters": {
        "albums": 1,
        "videos": 14,
        "audios": 0,
        "photos": 2,
        "friends": 1,
        "mutual_friends": 0,
        "followers": 0,
        "subscriptions": 0,
        "pages": 2
      }
    },
    "photos": {
      "count": 1,
      "items": [
        {
          "photo_id": 323470247,
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
            "count": 1,
            "items": [
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

    def setUp(self) -> None:
        super().setUp()
        self.client = Client()
        self.client.post(reverse('main:login_page'), {
            'username': self.user.username,
            'password': 'top_secret'
        }, follow=True)


class AddUserTest(AuthorizedMainTest):
    """
    Tests for 'add_user' and 'add_user_result' pages
    """

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
        domain = FIRST_USER['main_info']['domain']

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
        self.assertEqual(user_info, FIRST_USER)


class UserInfoTest(AuthorizedMainTest):

    def setUp(self) -> None:
        super().setUp()
        date = datetime.now().timetuple()
        self.info = FIRST_USER
        self.info['date'] = {
            'year': date[0],
            'month': date[1],
            'day': date[2],
            'hour': date[3],
            'minutes': date[4]
        }
        self.info['_id'] = str(ObjectId())
        storage = mongo.VKInfoStorage.connect(db=mongo.get_conn())
        storage.add_user(user=self.info)

    def test_user_info_get_method(self):
        response = self.client.get(reverse('main:user_info'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Get info')
        self.assertContains(response, 'Enter user domain:')

    def test_get_user_info(self) -> None:
        """
        Test for adding user by web interface
        """
        domain = self.info['main_info']['domain']
        response = self.client.post(reverse('main:get_user_info'), {
            'domain': domain
        }, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Information about')
        self.assertContains(response, 'First User')

        for friend in self.info['friends']['items']:
            self.assertContains(response, friend['id'])
        for follower in self.info['followers']['items']:
            self.assertContains(response, follower['id'])
        for group in self.info['groups']['items']:
            self.assertContains(response, group['id'])
        for post in self.info['wall']['items']:
            self.assertContains(response, post['post_id'])
        for photo in self.info['photos']['items']:
            self.assertContains(response, photo['photo_id'])


class UserChangesTest(AuthorizedMainTest):

    def setUp(self) -> None:
        super().setUp()
        date = datetime.now().timetuple()

        self.info = FIRST_USER
        self.info['date'] = {
            'year': date[0],
            'month': date[1],
            'day': date[2],
            'hour': date[3],
            'minutes': date[4]
        }
        self.info['_id'] = str(ObjectId())

        self.changed_info = CHANGED_FIRST_USER
        self.changed_info['date'] = {
            'year': date[0],
            'month': date[1],
            'day': date[2],
            'hour': date[3],
            'minutes': date[4] + 1
        }
        self.changed_info['_id'] = str(ObjectId())

        storage = mongo.VKInfoStorage.connect(db=mongo.get_conn())
        storage.add_user(user=self.info)
        storage.add_user(user=self.changed_info)

    def test_get_changes_get_method(self):
        response = self.client.get(reverse('main:get_changes'), follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Get changes')
        self.assertContains(response, 'Enter user domain:')

    def test_get_changes_dates(self) -> None:
        """
        Test for getting dates user info was collected by web interface
        """
        domain = self.info['main_info']['domain']
        response = self.client.post(reverse('main:get_dates'), {
            'domain': domain
        }, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Get dates')
        self.assertContains(response, self.info['date'])
        self.assertContains(response, self.changed_info['date'])

    def test_get_changes(self) -> None:
        """
        Test for getting user account info changes by web interface
        """
        domain = self.info['main_info']['domain']
        response = self.client.post(reverse('main:get_user_changes'), {
            'domain': domain,
            'date1': self.info['date'],
            'date2': self.changed_info['date']
        }, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'First User')
        self.assertContains(response, 'account changes')

        deleted_friend = self.info['friends']['items'][1]
        deleted_follower = self.info['followers']['items'][0]
        deleted_group = self.info['groups']['items'][1]
        deleted_photo = self.info['photos']['items'][1]
        new_like_info = '<a href="https://vk.com/id771335">SecondFriendName SecondFriendSurname</a>[NEW]'

        self.assertContains(response, deleted_friend['id'])
        self.assertContains(response, deleted_follower['id'])
        self.assertContains(response, deleted_group['id'])
        self.assertContains(response, deleted_photo['photo_id'])
        self.assertContains(response, new_like_info)
