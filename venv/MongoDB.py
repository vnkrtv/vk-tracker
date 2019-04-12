from pymongo import MongoClient

class MongoDB(object):

    def __init__(self, host='localhost', port=27017):
        self._client = MongoClient(host, port)
        self._db = self._client.vk_data

    def addUser(self, user):
        id = user['main_info']['id']
        date = "{hour:02}.{minutes:02} {day}.{month:02}.{year}".format(**user['date'])

        if self._db.find({'user_id' : id}) != {}:
            self._db.update({'user_id' : id}, {'$push': {'dates': {date: user}}})
        else:
            self._db.insert({'user_id': id, 'dates': [{date: user}]})