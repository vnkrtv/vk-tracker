import traceback
import json

from django.shortcuts import render
from requests.exceptions import ConnectionError
from .vk_search import *
from MongoDB import *


def get_search_params(request):
    return render(request, 'vksearch/search/searchPage.html')


def get_result(request):
    params = dict(request.POST)
    print(params)
    info = {}

    try:
        pass
    except Exception:
        info['error'] = traceback.format_exc()

    return render(request, 'vksearch/search/resultPage.html', info)


def get_new_philter_countries(request):
    with open('config/config.json', 'r') as file:
        config = json.load(file)

    mdb = VKDatabaseMongoDB(host=config['mdb_host'], port=config['mdb_port'])
    info = {
        'countries': mdb.get_countries()['items']
    }
    return render(request, 'vksearch/add_philter/getCountry.html', info)


def get_new_philter_region(request):
    with open('config/config.json', 'r') as file:
        config = json.load(file)

    country_id = request.POST['country'][0]
    mdb = VKDatabaseMongoDB(host=config['mdb_host'], port=config['mdb_port'])
    info = {
        'regions': mdb.get_regions(country_id=country_id)['items'],
        'country_id': country_id
    }
    return render(request, 'vksearch/add_philter/getRegion.html', info)


def get_new_philter_cities(request):
    with open('config/config.json', 'r') as file:
        config = json.load(file)

    region_id = request.POST['region'][0]
    country_id = request.POST['country_id'][0]
    cities_num = request.POST['cities_num'][0]

    mdb = VKDatabaseMongoDB(host=config['mdb_host'], port=config['mdb_port'])
    info = {
        'cities': mdb.get_cities(country_id=country_id, region_id=region_id)['items'],
        'cities_num': list(range(cities_num)),
        'country_id': country_id,
        'region_id': region_id
    }
    return render(request, 'vksearch/add_philter/getCities.html', info)


def get_new_philter_universities(request):
    return render(request, 'vksearch/add_philter/getUniversities.html')


def get_new_philter_friends_and_groups(request):
    return render(request, 'vksearch/add_philter/getGroupsAndFriends.html')


def add_new_philter(request):
    return render(request, 'vksearch/add_philter/addPhilter.html')


def get_new_philte(request):
    req = dict(request.POST)

    keys = ['allowed_groups', 'friends_list', 'countries']
    info = {}
    for key in keys:
        if key in req:
            info[key] = True if req[key] == ['on'] else False
        else:
            info[key] = False

    for key in keys:
        info[key + '_num'] = [i for i in range(int(req[key + '_num'][0]))]

    with open('config/config.json', 'r') as file:
        config = json.load(file)

    #mdb = VKDatabaseMongoDB(host=config['mdb_host'], port=config['mdb_port'])

    #info['countries_list'] = mdb
    info['cities_list'] = []
    info['universities_list'] = []

    return render(request, 'vksearch/add_philter/getCountry.html', info)


def get_new_philter(request):
    info = {
        'philter_name': request.POST['philter_name'][0]
    }
    return render(request, 'vksearch/add_philter/getNewPhilter.html', info)