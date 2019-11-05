import vk
import json
from time import sleep
from pymongo import MongoClient


class VKMongoDB(object):

    def __init__(self, host='localhost', port=27017):
        self._client = MongoClient(host, port) if port else MongoClient(host)
        self._db = self._client.vk.vk_data

    def add_user(self, user):
        """

        :param user: json with vk user information
        """
        id = user['main_info']['id']
        domain = user['main_info']['domain']
        date = "{hour:02}-{minutes:02} {day}-{month:02}-{year}".format(**user['date'])

        if self._db.find_one({'user_id' : id}):
            self._db.find_one_and_update({'user_id' : id}, {'$push': {'dates': {date: user}}})
        else:
            self._db.insert_one({'user_id': id, 'domain': domain, 'dates': [{date: user}]})

    def check_domain(self, domain):
        """

        :param domain: vk user domain
        :return: True if user exist in db, False else
        """
        if self._db.find_one({'domain': domain}):
            return True
        return False

    def get_fullname(self, domain):
        """

        :param domain: vk user domain
        :return: str '${first_name} ${last_name}'
        """
        if self.check_domain(domain):
            info = list(self._db.find_one({'domain': domain})['dates'][-1].values())[0]['main_info']
            return info['first_name'] + ' ' + info['last_name']
        else:
            return ''

    def load_user_info(self, id=0, domain='', date=''):
        """

        :param id: vk user id (if input)
        :param domain: vk user domain (if input)
        :param date: vk user information collected this date (if not input - latest info)
        :return: dict with vk user information
        """
        if id != 0:
            if date:
                info = {}
                for inf in self._db.find_one({'user_id': id})['dates']:
                    for d in inf:
                        if d == date:
                            info = inf[date]
                return info
            else:
                info = self._db.find_one({'user_id': id})
                return list(info['dates'][-1].values())[0]

        elif domain != '':
            if date:
                info = {}
                for inf in self._db.find_one({'domain': domain})['dates']:
                    for d in inf:
                        if d == date:
                            info = inf[date]
                return info
            else:
                info = self._db.find_one({'domain': domain})
                return list(info['dates'][-1].values())[0]

    def get_user_info_dates(self, id=0, domain=''):
        """

        :param id: vk user id
        :param domain: vk user domain
        :return: list of dates when vk user information was collected
        """
        if id != 0:
            dates = [date for date in list(self._db.find_one({'user_id': id})['dates'])]
            return [list(date.keys())[0] for date in dates]
        elif domain != '':
            dates = [date for date in list(self._db.find_one({'domain': domain})['dates'])]
            return [list(date.keys())[0] for date in dates]


class InstMongoDB(object):

    def __init__(self, host='localhost', port=27017):
        self._client = MongoClient(host, port)
        self._db = self._client.inst.inst_data

    def add_user(self, user):
        """

        :param user: json with instagram user information
        """
        id = user['main_info']['id']
        domain = user['main_info']['domain']
        date = "{hour:02}-{minutes:02} {day}-{month:02}-{year}".format(**user['date'])

        if self._db.find_one({'user_id' : id}):
            self._db.find_one_and_update({'user_id' : id}, {'$push': {'dates': {date: user}}})
        else:
            self._db.insert_one({'user_id': id, 'domain': domain, 'dates': [{date: user}]})

    def check_domain(self, domain):
        """

        :param username: instagram username
        :return: True if user exist in db, False else
        """
        if self._db.find_one({'username': domain}):
            return True
        return False

    def get_fullname(self, domain):
        """

        :param domain: vk user domain
        :return: str '${first_name} ${last_name}'
        """
        if self.check_domain(domain):
            info = list(self._db.find_one({'domain': domain})['dates'][-1].values())[0]['main_info']
            return info['first_name'] + ' ' + info['last_name']
        else:
            return ''

    def load_user_info(self, id=0, domain='', date=''):
        """

        :param id: vk user id (if input)
        :param domain: vk user domain (if input)
        :param date: vk user information collected this date (if not input - latest info)
        :return: dict with vk user information
        """
        if id != 0:
            if date:
                info = {}
                for inf in self._db.find_one({'user_id': id})['dates']:
                    for d in inf:
                        if d == date:
                            info = inf[date]
                return info
            else:
                info = self._db.find_one({'user_id': id})
                return list(info['dates'][-1].values())[0]

        elif domain != '':
            if date:
                info = {}
                for inf in self._db.find_one({'domain': domain})['dates']:
                    for d in inf:
                        if d == date:
                            info = inf[date]
                return info
            else:
                info = self._db.find_one({'domain': domain})
                return list(info['dates'][-1].values())[0]

    def get_user_info_dates(self, id=0, domain=''):
        """

        :param id: vk user id
        :param domain: vk user domain
        :return: list of dates when vk user information was collected
        """
        if id != 0:
            dates = [date for date in list(self._db.find_one({'user_id': id})['dates'])]
            return [list(date.keys())[0] for date in dates]
        elif domain != '':
            dates = [date for date in list(self._db.find_one({'domain': domain})['dates'])]
            return [list(date.keys())[0] for date in dates]


class VKSearchFilterMongoDB(object):

    def __init__(self, host='localhost', port=27017):
        self._client = MongoClient(host, port)
        self._db = self._client.vk.search_filters

    def load_philter(self, filter):
        """

        :param filter: {
            'name': filter_name(str),
            'country_id': country_id(int),
            'cities': cities_ids(list of int),
            'universities': universities_ids(list of int),
            'friends': friends_domains(list of str),
            'groups': groups_ids(list of int)
        }
        """
        self._db.insert_one({'name': filter['name'], 'filter': filter})
        if self._db.find_one({'filters': {'$exists': True}}):
            #костыль, лень что-то придумать
            #TODO: переписать это дерьмо
            filters = self._db.find_one({'filters': {'$exists': True}})['filters']

            self._db.delete_one({'filters': {'$exists': True}})
            filters.append(filter['name'])
            self._db.insert_one({'filters': filters})
        else:
            self._db.insert_one({'filters': [filter['name']]})

    def get_all_philters_names(self):
        filters = self._db.find_one({'filters': {'$exists': True}})
        return filters['filters'] if filters else []


    def get_filter(self, filter_name):
        """

        :param filter_name: str
        :return: {
            'name': filter_name(str),
            'country_id': country_id(int),
            'cities': cities_ids(list of int),
            'universities': universities_ids(list of int),
            'friends': friends_domains(list of str),
            'groups': groups_ids(list of int)
        }
        """
        res = self._db.find_one({'name': filter_name})
        return res['filter'] if 'filter' in res else None

    def delete_philter(self, filter_name):
        filters = self._db.find_one({'filters': {'$exists': True}})['filters']

        self._db.delete_one({'filters': {'$exists': True}})
        filters.remove(filter_name)
        self._db.insert_one({'filters': filters})

        self._db.remove({'name': filter_name})


class VKDatabaseMongoDB(object):

    def __init__(self, host='localhost', port=27017):
        self._client = MongoClient(host, port)
        self._db = self._client.vk.database

    def load_countries(self, countries_info):
        """

        :param countries_info: { 'count": <>, 'items': { ... } }
        :return:
        """
        self._db.insert_one({'countries': countries_info})

    def get_countries(self):
        countries = self._db.find_one({'countries': {'$exists': True}})['countries']
        return countries

    def load_regions(self, regions_info, country_id):
        """

        :param country_id:
        :param regions_info:
        :return:
        """
        self._db.insert_one({'regions': {str(country_id): regions_info}})

    def get_regions(self, country_id):
        regions = self._db.find_one({'regions': {'$exists': True}})['regions']
        return regions[str(country_id)]

    def load_cities(self, cities_info, country_id, region_id):
        self._db.insert_one({'cities': {str(country_id): {str(region_id): cities_info}}})

    def get_cities(self, country_id, region_id):
        cities = self._db.find_one({'cities': {'$exists': True}})['cities']
        return cities[str(country_id)][str(region_id)]

    def load_universities(self, universities_info, country_id, city_id):
        """

        :param universities_info:
        :param country_id:
        :param city_id:
        :return:
        """
        self._db.insert_one({'universities': {
            str(country_id): {
                str(city_id): universities_info,
            }
        }})

    def get_all_universities(self):
        universities_list = self._db.find_one({'universities': {'$exists': True}})['universities']
        return universities_list

    def get_universities(self, country_id, city_id):
        """

        :param country_id:
        :param city_id:
        :return:
        """
        universities_list = self._db.find_one({'universities': {'$exists': True}})['universities']
        return universities_list[str(country_id)][str(city_id)]

    def load_schools(self, schools_info, city_id):
        """

        :param schools_info:
        :param city_id:
        """
        self._db.insert_one({'schools': {
            str(city_id): schools_info
        }})

    def get_all_schools(self):
        schools_list = self._db.find_one({'schools': {'$exists': True}})['schools']
        return schools_list

    def get_schools(self, city_id):
        """

        :param city_id:
        :return:
        """
        schools_list = self._db.find_one({'schools': {'$exists': True}})['schools']
        return schools_list[str(city_id)]

    def get_all(self):
        with open('data.json', 'w') as file:
            for data in self._db.find({}):
                data.pop('_id')
                json.dump(data, file, indent=2)

    def update_base(self, vk_token):
        """

        :param vk_token:
        :return:
        """
        with open('config/config.json', 'r') as file:
            token = json.load(file)['vk_token']
        session = vk.API(vk.Session(access_token=token))
        token_v = 5.102
        timeout = 0.34
        #RU, UA, BR,  KZ
        CIS_countries = [1, 2, 3, 4]

        countries = session.database.getCountries(need_all=1, count=1000, v=token_v)
        sleep(timeout)
        self.load_countries(countries)

        for country_id in CIS_countries:
            regions = session.database.getRegions(country_id=country_id, count=100, v=token_v)
            sleep(timeout)
            self.load_regions(regions, country_id)

            for region in regions['items']:
                region_id = region['id']
                cities = session.database.getCities(country_id=1, region_id=region_id, need_all=1, count=1000, v=token_v)
                sleep(timeout)
                self.load_cities(cities, country_id, region_id)

                for city in cities['items']:
                    city_id = city['id']

                    universities_info = session.database.getSchools(q='', city_id=city_id, count=10000, v=token_v)
                    sleep(timeout)
                    self.load_universities(universities_info, country_id, city_id)

                    schools_info = session.database.getSchools(q='', city_id=city_id, count=10000, v=token_v)
                    sleep(timeout)
                    self.load_schools(schools_info, city_id)
