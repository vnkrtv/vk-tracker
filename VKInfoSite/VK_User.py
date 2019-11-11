import vk


class VK_User(object):

    def __init__(self, token, domain):
        self._token = token
        self._user = vk.API(vk.Session(access_token=token))
        self._domain = self._user.users.get(user_ids=domain, fields='domain', v='5.65')[0]['domain']

        if self._domain != domain:
            raise Exception('wrong domain')

        self._id = self._user.users.get(user_ids=domain, v='5.65')[0]['id']
        self._user_name = self._user.users.get(user_ids=domain, v='5.65')[0]['first_name']
        self._user_surname = self._user.users.get(user_ids=domain, v='5.65')[0]['last_name']

    def get_first_name(self):
        return self._user_name

    def get_last_name(self):
        return self._user_surname

    def get_id(self):
        return self._id

    def get_domain(self):
        return self._domain
