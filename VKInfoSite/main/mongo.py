# pylint: disable=too-few-public-methods, invalid-name, global-statement
"""Custom classes for working with MongoDB without Django ORM"""
from urllib.parse import quote_plus
import pymongo
from django.conf import settings

_db_conn: pymongo.database.Database = None


def set_conn(host: str, port: int, db_name: str) -> None:
    """
    Establish user connection to MongoDB database 'db_name'

    :param host: MongoDB host
    :param port: MongoDB port
    :param db_name: MongoDB database name
    """
    global _db_conn
    if settings.DATABASES['default']['USER']:
        _db_conn = pymongo.MongoClient('mongodb://{user}:{pwd}@{host}:{port}'.format(
            user=quote_plus(settings.DATABASES['default']['USER']),
            pwd=quote_plus(settings.DATABASES['default']['PASSWORD']),
            host=host,
            port=port
        ))[db_name]
    else:
        _db_conn = pymongo.MongoClient(host, port)[db_name]


def get_conn() -> pymongo.database.Database:
    """
    Get user connection to MongoDB database 'db_name'

    :return: Database - connection to database
    """
    global _db_conn
    if not _db_conn:
        set_conn(
            host=settings.DATABASES['default']['HOST'],
            port=settings.DATABASES['default']['PORT'],
            db_name=settings.DATABASES['default']['NAME'])
    return _db_conn


class MongoDB:
    """Base class for classes working with MongoDB"""

    _db: pymongo.database.Database
    _col: pymongo.collection.Collection

    def set_collection(self, db: pymongo.database.Database, collection_name: str) -> None:
        """
        Get connection to MongoDB database and connect to current collection 'collection_name'

        :param db: MongoDB Database
        :param collection_name: name of database collection
        """
        self._db = db
        self._col = db[collection_name]


class VKInfoStorage(MongoDB):
    """
    Class for working with vk users
    information stored in MongoDB
    """

    @staticmethod
    def connect(db: pymongo.database.Database):
        """
        Establish connection to database collection 'info'

        :param db: Database - connection to MongoDB database
        :return: VKInfoStorage object
        """
        storage = VKInfoStorage()
        storage.set_collection(
            db=db,
            collection_name='info')
        return storage

    def add_user(self, user: dict) -> None:
        """
        Add user to database collection 'info'

        :param user: <dict>
          {
            'main_info': { ... },
            'friends': { ... },
            'followers': { ... },
            'groups': { ... },
            'wall': { ... },
            'photos': { ... },
            'date': { ... }
          }
        """
        user['id'] = user['main_info']['id']
        user['domain'] = user['main_info']['domain']
        user['date'] = "{hour:02}-{minutes:02} {day}-{month:02}-{year}".format(**user['date'])
        self._col.insert_one(user)

    def check_domain(self, domain: str) -> bool:
        """
        Check if user's contained in DB

        :param domain: vk user domain
        :return: True if user exist in db, False else
        """
        if self._col.find_one({'domain': domain}):
            return True
        return False

    def get_fullname(self, domain: str) -> str:
        """
        VK user fullname

        :param domain: vk user domain
        :return: '${first_name} ${last_name}'
        """
        if self.check_domain(domain):
            info = self._col.find_one({'domain': domain})['main_info']
            return info['first_name'] + ' ' + info['last_name']
        return ''

    def get_user(self, _id: int = 0, domain: str = '', date: str = '') -> dict:
        """

        :param _id: vk user id (if passed)
        :param domain: vk user domain (if passed)
        :param date: date when information was collected (if not passed - latest info)
        :return: dict with vk user information
        """
        info = {}
        if _id != 0:
            if date:
                info = self._col.find_one({'id': _id, 'date': date})
            else:
                info = self._col.find_one({'id': _id})
        elif domain != '':
            if date:
                info = self._col.find_one({'domain': domain, 'date': date})
            else:
                info = self._col.find_one({'domain': domain})
        return info if info else {}

    def get_user_info_dates(self, _id=0, domain='') -> list:
        """
        Dates when info about user was collected

        :param _id: vk user id
        :param domain: vk user domain
        :return: list of dates when info was collected
        """
        info_list = []
        if _id != 0:
            info_list = self._col.find({'id': _id})
        if domain != '':
            info_list = self._col.find({'domain': domain})
        return [info['date'] for info in info_list] if info_list else []
