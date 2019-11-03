#plotlyx

import SQLiteDB as sql
import vk
import json

if __name__ == '__main__':
    with open('config/default_config.json', 'r') as file:
        token = json.load(file)['vk_token']

    sql.SQLiteDB().update_base(token)

