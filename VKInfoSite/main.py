#plotlyx

import SQLiteDB as sql
import vk
import json

if __name__ == '__main__':
    with open('config/default_config.json', 'r') as file:
        token = json.load(file)['vk_token']

    session = vk.API(vk.Session(access_token=token))
    response = session.database.getCountries(nead_all=1, count=1000, v=5.102)
    print(sql.SQLiteDB().get_countries())
    sql.SQLiteDB().load_countries(response)
    print(sql.SQLiteDB().get_countries())

