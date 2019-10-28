import vk
import json

from MongoDB import *
#from .mongodb import *

def search(**kwargs):
    """

    :param q:
    :param age_from:
    :param age_to:
    :param sex:
    :param city:
    :param country:
    :param university:
    :param has_photo:
    :param group_id:
    :return:
    """
    with open('config/config.json', 'r') as file:
        token = json.load(file)['vk_token']

    session = vk.API(vk.Session(access_token=token))
    response = session.users.search(**kwargs)
    return response


if __name__ == '__main__':
    mdb = VKDatabaseMongoDB()
    #with open('config/config.json', 'r') as file:
    #    token = json.load(file)['vk_token']
    mdb.get_all()

    q = {
        'q': 'Александра',
        'age_from': 18,
        'age_to': 20,
        'city': 1,
        'university': 1,
        'count': 30,
        'v': 5.102
    }
    #print(search(**q))
