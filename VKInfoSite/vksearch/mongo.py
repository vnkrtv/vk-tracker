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


class VKSearchFiltersStorage(MongoDB):

    @staticmethod
    def connect_to_mongodb(host: str, port, db_name: str):
        """
        Establish connection to mongodb database 'db_name', collection 'search_filters'

        :param host: MongoDB host
        :param port: MongoDB port
        :param db_name: MongoDB name
        :return: VKSearchFiltersStorage object
        """
        obj = VKSearchFiltersStorage()
        obj._client, obj._db, obj._col = MongoDB.get_connection(
            host=host,
            port=port,
            db_name=db_name,
            collection_name='filters'
        )
        return obj

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
