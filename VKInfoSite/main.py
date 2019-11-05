#plotlyx

import SQLiteDB as sql
import vk
import json

if __name__ == '__main__':
    with open('config/default_config.json', 'r') as file:
        token = json.load(file)['vk_token']

    token_v = 5.102
    session = vk.API(vk.Session(access_token=token))
    cities = session.database.getCities(country_id=1, region_id=1053480, need_all=1, count=1000,
                                        v=token_v)
    print(list(filter(lambda d: d['id'] == 1, cities['items'])))
    #print(sql.SQLiteDB(db_file='../db/VKDatabase.db').get_countries())
