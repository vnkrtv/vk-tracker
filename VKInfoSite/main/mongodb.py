import vk
import json
from time import sleep
from pymongo import MongoClient


class MongoDB:
    """
    Class for getting connection to MongoDB

    _client: MongoClient() object
    _db: MongoDB database
    _col: MongoDB collection
    """

    _client = None
    _db = None
    _col = None

    @staticmethod
    def get_connection(host: str, port, db_name: str, collection_name: str) -> tuple:
        """
        Establish connection to mongodb database 'db_name', collection 'questions'

        :param host: MongoDB host
        :param port: MongoDB port
        :param db_name: database name
        :param collection_name: collection name
        :return: tuple of (MongoClient, db, collection)
        """
        client = MongoClient(host, int(port))
        db = client[db_name]
        col = db[collection_name]
        return client, db, col


class VKInfoStorage(MongoDB):

    @staticmethod
    def connect_to_mongodb(host: str, port, db_name: str):
        """
        Establish connection to mongodb database 'db_name', collection 'info'

        :param host: MongoDB host
        :param port: MongoDB port
        :param db_name: MongoDB name
        :return: VKInfoStorage object
        """
        obj = VKInfoStorage()
        obj._client, obj._db, obj._col = MongoDB.get_connection(
            host=host,
            port=port,
            db_name=db_name,
            collection_name='info'
        )
        return obj

    def add_user(self, user) -> None:
        """

        :param user: json with vk user information
        """
        user['id'] = user['main_info']['id']
        user['domain'] = user['main_info']['domain']
        user['date'] = "{hour:02}-{minutes:02} {day}-{month:02}-{year}".format(**user['date'])
        self._db.insert_one(user)

    def check_domain(self, domain) -> bool:
        """

        :param domain: vk user domain
        :return: True if user exist in db, False else
        """
        if self._db.find_one({'domain': domain}):
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
        else:
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
                info = self._col.find_one({'user_id': _id, 'date': date})
            else:
                info = self._col.find_one({'user_id': _id})
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
        if id != 0:
            info_list = self._col.find_many({'user_id': _id})
        elif domain != '':
            info_list = self._col.find_many({'domain': domain})
        return [info['date'] for info in info_list] if info_list else []


class VKOnlineInfoStorage(MongoDB):

    @staticmethod
    def connect_to_mongodb(host: str, port, db_name: str):
        """
        Establish connection to mongodb database 'db_name', collection 'online_info'

        :param host: MongoDB host
        :param port: MongoDB port
        :param db_name: MongoDB name
        :return: VKOnlineInfoStorage object
        """
        obj = VKOnlineInfoStorage()
        obj._client, obj._db, obj._col = MongoDB.get_connection(
            host=host,
            port=port,
            db_name=db_name,
            collection_name='online_info'
        )
        return obj

    def load_activity(self, _id: str, last_seen_timestamp: int, online: bool, platform: int) -> None:
        info = 0b00000000000000000000000000000000

        # first bit - online info
        info |= (online << 31)

        # 2-5 bits - platform
        info |= (platform << 28)

        if self._db.find_one({'user_id': id}):
            # 5 - 32 bits - info
            info |= (last_seen_timestamp - self._db.find_one({'user_id': id})['start_monitoring_timestamp'])
            self._db.find_one_and_update({'user_id': id}, {'$push': {
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

        :param id:
        :return: tuple of (start_monitoring_timestamp, activity info list) if user is tracked; None, None else
        """
        data = self._db.find_one({'user_id': _id})
        if data:
            return data['start_monitoring_timestamp'], data['activity']
        else:
            return None, None
