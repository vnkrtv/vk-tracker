# pylint: disable=too-few-public-methods, invalid-name
import pymongo
from urllib.parse import quote_plus
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
    """
    Base class for classes working with MongoDB

    _db:     MongoDB database
    _col:    MongoDB collection
    """

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

    def add_user(self, user) -> None:
        """

        :param user: json with vk user information
        """
        user['id'] = user['main_info']['id']
        user['domain'] = user['main_info']['domain']
        user['date'] = "{hour:02}-{minutes:02} {day}-{month:02}-{year}".format(**user['date'])
        self._col.insert_one(user)

    def check_domain(self, domain) -> bool:
        """

        :param domain: vk user domain
        :return: True if user exist in db, False else
        """
        if self._col.find_one({'domain': domain}):
            return True
        return False

    def get_fullname(self, domain) -> str:
        """

        :param domain: vk user domain
        :return: str '${first_name} ${last_name}'
        """
        if self.check_domain(domain):
            info = self._col.find_one({'domain': domain})['main_info']
            return info['first_name'] + ' ' + info['last_name']
        return ''

    def get_user(self, _id: int = 0, domain: str = '', date: str = '') -> dict:
        """

        :param _id: vk user id (if input)
        :param domain: vk user domain (if input)
        :param date: vk user information collected this date (if not input - latest info)
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
        return info

    def get_user_info_dates(self, _id=0, domain='') -> list:
        """

        :param _id: vk user id
        :param domain: vk user domain
        :return: list of dates when vk user information was collected
        """
        info_list = []
        if _id != 0:
            info_list = self._col.find({'id': _id})
        if domain != '':
            info_list = self._col.find({'domain': domain})
        return [info['date'] for info in info_list] if info_list else []


class VKOnlineInfoStorage(MongoDB):

    @staticmethod
    def connect(db: pymongo.database.Database):
        """
        Establish connection to database collection 'online_info'

        :param db: Database - connection to MongoDB database
        :return: VKOnlineInfoStorage object
        """
        storage = VKOnlineInfoStorage()
        storage.set_collection(
            db=db,
            collection_name='info')
        return storage

    def load_activity(self, _id: str, last_seen_timestamp: int, online: int, platform: int) -> None:
        info = 0b00000000000000000000000000000000

        # first bit - online info
        info |= (online << 31)

        # 2-5 bits - platform
        info |= (platform << 28)

        if self._db.find_one({'id': id}):
            # 5 - 32 bits - info
            time = last_seen_timestamp - self._db.find_one({'id': id})['start_monitoring_timestamp']
            info |= time
            self._db.find_one_and_update({'id': id}, {'$push': {
                'activity': info
            }})
        else:
            self._db.insert_one({
                'user_id': _id,
                'start_monitoring_timestamp': last_seen_timestamp,
                'activity': [info]
            })

    def get_activity(self, _id: int) -> tuple:
        """

        :param _id:
        :return: tuple of (start_monitoring_timestamp, activity info list)
                 if user is tracked; None, None else
        """
        data = self._db.find_one({'user_id': _id})
        if data:
            return data['start_monitoring_timestamp'], data['activity']
        return None, None
