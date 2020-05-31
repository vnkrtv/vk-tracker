import sys


class VKOnlineInfoStorage(MongoDB):

    @staticmethod
    def connect(db: pymongo.database.Database):
        """
        Establish connection to database collection 'online_info'

        :param db: Database - connection to MongoDB database
        :return: VKOnlineInfoStorage object
        """
        storage = VKOnlineInfoStorage()
        storage.set_collection(
            db=db,
            collection_name='info')
        return storage

    def load_activity(self, _id: str, last_seen_timestamp: int, online: int, platform: int) -> None:
        info = 0b00000000000000000000000000000000

        # first bit - online info
        info |= (online << 31)

        # 2-5 bits - platform
        info |= (platform << 28)

        if self._db.find_one({'id': id}):
            # 5 - 32 bits - info
            time = last_seen_timestamp - self._db.find_one({'id': id})['start_monitoring_timestamp']
            info |= time
            self._db.find_one_and_update({'id': id}, {'$push': {
                'activity': info
            }})
        else:
            self._db.insert_one({
                'user_id': _id,
                'start_monitoring_timestamp': last_seen_timestamp,
                'activity': [info]
            })

    def get_activity(self, _id: int) -> tuple:
        """

        :param _id:
        :return: tuple of (start_monitoring_timestamp, activity info list)
                 if user is tracked; None, None else
        """
        data = self._db.find_one({'user_id': _id})
        if data:
            return data['start_monitoring_timestamp'], data['activity']
        return None, None


if __name__ == '__main__':
    with open('../vktoken/vktoken.json', 'r') as file:
        token = json.load(file)['vk_token']

    domain = sys.argv[1]
    try:
        user = VK_UserActivity(domain=domain, token=token)
        print('Start monitoring %s[%s]' % ((user.get_first_name() + ' ' + user.get_last_name()), domain))
    except Exception as e:
        print(e)
        exit(1)
    while True:
        user.check_user_activity()
        sleep(60)
