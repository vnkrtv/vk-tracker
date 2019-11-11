import datetime
import json

from VK_UserInfo import *
from MongoDB import VKActivityMongoDB
from config import *


class VK_UserActivity(VK_User):

    def __init__(self, token, domain):
        super(VK_UserActivity, self).__init__(token, domain)

    def check_user_activity(self):
        user = self._user.users.get(user_ids=self._domain, fields='last_seen,online', v='5.103')[0]

        is_online = user['online']
        last_seen_timestamp = user['last_seen']['time']
        last_seen_platform = user['last_seen']['platform']

        platform = {
            1: 'm.vk.com',
            2: 'iPhone app',
            3: 'iPad app',
            4: 'Android app',
            5: 'Windows Phone app',
            6: 'Windows 8 app',
            7: 'web (vk.com)',
            8: 'VK Mobile'
        }

        last_seen_time = datetime.datetime.fromtimestamp(last_seen_timestamp)
        strtime = time.strftime('%Y-%m-%d %H:%M:%S')
        time_dict = {
            'second': last_seen_time.second,
            'minute': last_seen_time.minute,
            'hour':   last_seen_time.hour,
            'day':    last_seen_time.day,
            'month':  last_seen_time.month,
            'year':   last_seen_time.year
        }
        self.load_activity(strtime, is_online, last_seen_platform)

    def load_activity(self, strtime, is_online, last_seen_platform):
        """

        :param strtime: '%Y-%m-%d %H:%M:%S'
        :param is_online: 1/0
        :param last_seen_platform:
        :return:
        """
        with open(CONFIG_FILE, 'r') as file:
            config = json.load(file)
            mdb = VKActivityMongoDB(host=config['mdb_host'], port=config['mdb_port'])
            mdb.load_activity(self._id, strtime, is_online, last_seen_platform)

    def get_activity(self):
        with open(CONFIG_FILE, 'r') as file:
            config = json.load(file)
            mdb = VKActivityMongoDB(host=config['mdb_host'], port=config['mdb_port'])
            activity = mdb.get_activity(self._id)
        return activity
