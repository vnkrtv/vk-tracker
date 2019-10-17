import os
import json

class InstUserInfo:

    def __init__(self, username):
        command = 'instagram-scraper --destination=. --media-types=none {}'
        output = os.popen(command.format(username))
        if 'ERROR: ' in output.read():
            raise Exception('Error getting user details for {}. Please verify that the user exists.'.format(username))
        else:
            self._user = username

    def get_info(self):
        command = 'instagram-scraper ' \
                  '--media-metadata ' \
                  '--profile-metadata ' \
                  '--include-location ' \
                  '--comments ' \
                  '--media-types=none ' \
                  '--destination=. {}'

        os.popen(command.format(self._user)).read()
        with open('./{}.json'.format(self._user), 'r') as file:
            data = json.load(file)

        os.popen('rm ./{}.json'.format(self._user))

        return data


if __name__ == '__main__':
    #print(InstUserInfo(username='van4ester__').get_info())