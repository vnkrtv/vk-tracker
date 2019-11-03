import sqlite3 as sql
from time import sleep


class SQLiteDB(object):

    def __init__(self, db_file="../db/VKDatabase.db"):
        self.conn = sql.connect(db_file)
        self.cursor = self.conn.cursor()

    def load_countries(self, countries_info):
        """


        :param countries_info: { 'count": <>, 'items': { ... } }
        :return:
        """
        try:
            self.cursor.execute('CREATE TABLE countries (id INT , title text)')
        except:
            pass
        countries = set([tuple(item.values()) for item in countries_info['items']])
        countries -= set(self.get_countries())
        self.cursor.executemany('INSERT INTO countries VALUES (?,?)', countries)
        self.conn.commit()

    def get_countries(self):
        countries = [item for item in self.cursor.execute('SELECT * FROM countries ORDER BY id')]
        return countries

    def load_regions(self, regions_info, country_id):
        """

        :param country_id:
        :param regions_info:
        :return:
        """
        try:
            self.cursor.execute(f'CREATE TABLE regions_{country_id} (id INT , title text)')
        except:
            pass
        regions = set([tuple(item.values()) for item in regions_info['items']])
        regions -= set(self.get_regions(country_id))
        self.cursor.executemany(f'INSERT INTO regions_{country_id} VALUES (?,?)', regions)
        self.conn.commit()

    def get_regions(self, country_id):
        regions = [item for item in self.cursor.execute(f'SELECT * FROM regions_{country_id} ORDER BY id')]
        return regions

    def load_cities(self, cities_info, country_id, region_id):
        """

        :param cities_info:
        :param country_id:
        :param region_id:
        :return:
        """
        try:
            self.cursor.execute(f'CREATE TABLE cities_{country_id}_{region_id} (id INT , title text)')
        except:
            pass
        cities = set([tuple(item.values()) for item in cities_info['items']])
        cities -= set(self.get_cities(country_id, region_id))
        self.cursor.executemany(f'INSERT INTO cities_{country_id}_{region_id} VALUES (?,?)', cities)
        self.conn.commit()

    def get_cities(self, country_id, region_id):
        """

        :param country_id:
        :param region_id:
        :return:
        """
        cities = [item for item in self.cursor.execute(f'SELECT * FROM cities_{country_id}_{region_id} ORDER BY id')]
        return cities

    def load_universities(self, universities_info, country_id, city_id):
        """

        :param universities_info:
        :param country_id:
        :param city_id:
        :return:
        """
        try:
            self.cursor.execute(f'CREATE TABLE universities_{country_id}_{city_id} (id INT , title text)')
        except:
            pass
        universities = set([tuple(item.values()) for item in universities_info['items']])
        universities -= set(self.get_universities(country_id, city_id))
        self.cursor.executemany(f'INSERT INTO universities_{country_id}_{city_id} VALUES (?,?)', universities)
        self.conn.commit()

    def get_universities(self, country_id, city_id):
        """

        :param country_id:
        :param city_id:
        :return:
        """
        universities = [item for item in self.cursor.execute(f'SELECT * FROM universities_{country_id}_{city_id} ORDER BY id')]
        return universities

    def load_schools(self, schools_info, city_id):
        """

        :param schools_info:
        :param city_id:
        """
        try:
            self.cursor.execute(f'CREATE TABLE schools_{city_id} (id INT , title text)')
        except:
            pass
        schools = set([tuple(item.values()) for item in schools_info['items']])
        schools -= set(self.get_schools(city_id))
        self.cursor.executemany(f'INSERT INTO schools_{city_id} VALUES (?,?)', schools)
        self.conn.commit()

    def get_schools(self, city_id):
        """

        :param city_id:
        :return:
        """
        schools = [item for item in self.cursor.execute(f'SELECT * FROM schools_{city_id} ORDER BY id')]
        return schools

    def update_base(self, vk_token):
        """

        :param vk_token:
        :return:
        """
        session = vk.API(vk.Session(access_token=vk_token))
        token_v = 5.102
        timeout = 0.34
        # RU, UA, BR, KZ
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
                cities = session.database.getCities(country_id=1, region_id=region_id, need_all=1, count=1000,
                                                    v=token_v)
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
