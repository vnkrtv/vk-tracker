from pymongo import MongoClient

class MongoDB(object):

    def __init__(self, host='localhost', port=27017):
        self._client = MongoClient(host, port)
        self._db = self._client.vk.vk_data

    def addUser(self, user):
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


    def checkDomain(self, domain):
        """

        :param domain: vk user domain
        :return: True if user exist in db, False else
        """
        if self._db.find_one({'domain': domain}):
            return True
        return False


    def getFullname(self, domain):
        """

        :param domain: vk user domain
        :return: str '${first_name} ${last_name}'
        """
        if self.checkDomain(domain):
            info = list(self._db.find_one({'domain': domain})['dates'][-1].values())[0]['main_info']
            return info['first_name'] + ' ' + info['last_name']
        else:
            return ''


    def loadUserInfo(self, id=0, domain='', date=''):
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


    def getUserDates(self, id=0, domain=''):
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
