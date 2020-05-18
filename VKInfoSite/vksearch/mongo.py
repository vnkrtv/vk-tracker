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


class VKSearchFiltersStorage(MongoDB):

    @staticmethod
    def connect(db: pymongo.database.Database):
        """
        Establish connection to database collection 'filters'

        :param db: Database - connection to MongoDB database
        :return: VKSearchFiltersStorage object
        """
        storage = VKSearchFiltersStorage()
        storage.set_collection(
            db=db,
            collection_name='filters')
        return storage

    def add_filter(self, _filter: dict) -> None:
        """

        :param _filter: <dict>
            {
                'name': filter_name(str),
                'country_id': country_id(int),
                'cities': cities_ids(list of int),
                'cities_titles': cities_names(list of str),
                'universities': universities_ids(list of int),
                'friends': friends_domains(list of str),
                'groups': groups_ids(list of int)
            }
        """
        self._col.insert_one(_filter)

    def get_all_philters_names(self) -> list:
        filters = self._col.find({})
        return [_filter['name'] for _filter in filters] if filters else []

    def get_filter(self, filter_name: str) -> dict:
        """

        :param filter_name: str
        :return: {
            'name': filter_name(str),
            'country_id': country_id(int),
            'cities': cities_ids(list of int),
            'cities_titles': cities_names(list of str),
            'universities': universities_ids(list of int),
            'friends': friends_ids(list of int),
            'groups': groups_ids(list of int)
        }
        """
        _filter = self._col.find_one({'name': filter_name})
        return _filter

    def delete_philter(self, filter_name: str) -> None:
        self._col.delete_one({'name': filter_name})
