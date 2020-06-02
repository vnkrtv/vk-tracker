# pylint: disable=invalid-name
"""Class for working with MongoDB without Django ORM"""
import pymongo
from main.mongo import MongoDB


class VKSearchFiltersStorage(MongoDB):
    """Class for working with search filters"""

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

    def add_filter(self, new_filter: dict) -> None:
        """
        Add search filter to DB

        :param new_filter: dict
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
        self._col.insert_one(new_filter)

    def get_all_philters_names(self) -> list:
        """
        Get all search filters

        :return: list of filters names
        """
        filters = self._col.find({})
        return [_filter['name'] for _filter in filters] if filters else []

    def get_filter(self, filter_name: str) -> dict:
        """
        Get search filter by its name

        :param filter_name: str
        :return: dict
            {
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
        return _filter if _filter else {}

    def delete_philter(self, filter_name: str) -> None:
        """
        Delete search filter by its name

        :param filter_name: str
        """
        self._col.delete_one({'name': filter_name})
