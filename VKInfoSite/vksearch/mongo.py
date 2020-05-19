import pymongo
from main.mongo import MongoDB


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
