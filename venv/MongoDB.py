from pymongo import MongoClient

class MongoDB(object):

    def __init__(self, host='localhost', port=27017):
        self._client = MongoClient(host, port)
        self._db = self._client.vk.vk_data

    def addUser(self, user):
        id = user['main_info']['id']
        domain = user['main_info']['domain']
        date = "{hour:02}-{minutes:02} {day}-{month:02}-{year}".format(**user['date'])

        if self._db.find_one({'user_id' : id}):
            self._db.find_one_and_update({'user_id' : id}, {'$push': {'dates': {date: user}}})
        else:
            self._db.insert_one({'user_id': id, 'domain': domain, 'dates': [{date: user}]})

    def getDomain(self):
        return

    def loadUserInfo(self, id=0, domain='', date=''):
        try:
            if id != 0:
                if date:
                    info = {}
                    for d, inf in self._db.find_one({'user_id': id})['dates']:
                        if d == date:
                            info = inf
                    return info
                else:
                    info = self._db.find_one({'user_id': id})
                    return list(info['dates'][-1].values())[0]

            elif domain != '':
                if date:
                    info = {}
                    for d, inf in self._db.find_one({'domain': domain})['dates']:
                        if d == date:
                            info = inf
                    return info
                else:
                    info = self._db.find_one({'domain': domain})
                    return list(info['dates'][-1].values())[0]
        except:
            return {}

    def getUserDates(self, id=0, domain=''):
        try:
            if id != 0:
                dates = [date for d, inf in self._db.find_one({'user_id': id})['dates']]
                return dates
            elif domain != '':
                dates = [date for d, inf in self._db.find_one({'domain': domain})['dates']]
                return dates
        except:
            return []
