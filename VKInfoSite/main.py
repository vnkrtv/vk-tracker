#plotlyx

import SQLiteDB as sql
import vk
import json

if __name__ == '__main__':
    with open('config/default_config.json', 'r') as file:
        token = json.load(file)['vk_token']

    sql.SQLiteDB(db_file='../db/VKDatabase.db').update_base(token)

