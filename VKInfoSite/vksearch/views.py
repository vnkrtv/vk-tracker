import traceback
import json

from django.shortcuts import render
from requests.exceptions import ConnectionError
from .vk_search import *
from MongoDB import *
from SQLiteDB import *
from config import *


def vk_api(method, **kwargs):
    with open(CONFIG_FILE, 'r') as file:
        token = json.load(file)['vk_token']

    session = vk.API(vk.Session(access_token=token))
    return eval('session.' + method)(v=5.102, **kwargs)


def get_search_params(request):
    config = json.load(open(CONFIG_FILE, 'r'))
    mdb = VKSearchFilterMongoDB(host=config['mdb_host'], port=config['mdb_port'])
    info = {
        'filters': mdb.get_all_philters_names()
    }
    return render(request, 'vksearch/search/searchPage.html', info)


def get_search_result(request):
    params = dict(request.POST)
    print(params)
    info = {}

    try:
        pass
    except Exception:
        info['error'] = traceback.format_exc()

    return render(request, 'vksearch/search/resultPage.html', info)


def get_new_filter_countries(request):
    kwargs = {
        'need_all': 1,
        'count': 1000
    }
    countries = vk_api('database.getCountries', **kwargs)
    info = {
        'countries': [item for item in countries['items'] if item['id'] < 5]
    }
    return render(request, 'vksearch/add_philter/getCountry.html', info)


def get_new_filter_region(request):
    country_id = request.POST['country']
    regions_filter = request.POST['regions_filter']

    kwargs = {
        'country_id': country_id,
        'count': 1000
    }
    regions = vk_api('database.getRegions', **kwargs)

    info = {
        'regions': [item for item in regions['items'] if regions_filter in item['title']],
        'country_id': country_id
    }
    return render(request, 'vksearch/add_philter/getRegion.html', info)


def get_new_filter_cities(request):
    region_id = request.POST['region']
    country_id = request.POST['country_id']

    cities_num = int(request.POST['cities_num'])
    un_cities_num = int(request.POST['un_cities_num'])

    cities_filter = request.POST['cities_filter']
    un_cities_filter = request.POST['un_cities_filter']

    kwargs = {
        'country_id': country_id,
        'region_id': region_id,
        'count': 1000
    }
    req = vk_api('database.getCities', **kwargs)
    cities = [item for item in req['items'] if cities_filter in item['title']]
    un_cities = [item for item in req['items'] if un_cities_filter in item['title']]

    for city in [dict(title='Москва', id=1), dict(title='Санкт-Петербург', id=2), dict(title='Севастополь', id=185)]:
        if cities_filter in city['title']:
            cities.append(city)
        if un_cities_filter in city['title']:
            un_cities.append(city)

    info = {
        'cities': cities,
        'cities_num': list(range(cities_num)),
        'un_cities': un_cities,
        'un_cities_num': list(range(un_cities_num)),
        'country_id': country_id,
        'region_id': region_id
    }
    return render(request, 'vksearch/add_philter/getCities.html', info)


def get_new_filter_universities(request):
    cities = []
    for key in request.POST:
        if 'city' in key:
            cities.append(int(request.POST[key]))

    un_cities = []
    for key in request.POST:
        if 'un_city' in key:
            un_cities.append(int(request.POST[key]))

    info = {
        'cities': str(cities),
        'country_id': request.POST['country_id'],
    }

    if 'university_set' in request.POST:
        info['university_set'] = 1
        info['universities_num'] = range(int(request.POST['universities_num']))
    else:
        info['university_set'] = 0

    universities = []
    for city in un_cities:
        kwargs = {
            'q': request.POST['universities_filter'],
            'country_id': request.POST['country_id'],
            'city_id': city,
            'count': 1000
        }
        req = vk_api('database.getUniversities', **kwargs)
        universities += [item for item in req['items']]

    info['universities'] = universities
    return render(request, 'vksearch/add_philter/getUniversities.html', info)


def get_new_filter_friends_and_groups(request):
    print(request.POST)
    info = {
        'country_id': request.POST['country_id'],
        'cities': request.POST['cities'],
    }

    if 'friends_set' in request.POST:
        info['friends_set'] = 1
        info['friends_num'] = range(int(request.POST['friends_num']))
    else:
        info['friends_set'] = 0

    if 'groups_set' in request.POST:
        info['groups_set'] = 1
        info['groups_num'] = range(int(request.POST['groups_num']))
    else:
        info['groups_set'] = 0

    universities = []
    for key in request.POST:
        if 'univercity_' in key:
            universities.append(int(request.POST[key]))
    info['universities'] = str(universities)
    return render(request, 'vksearch/add_philter/getGroupsAndFriends.html', info)


def get_new_filter_name(request):
    info = {
        'country_id': request.POST['country_id'],
        'cities': request.POST['cities'],
        'universities': request.POST['universities']
    }
    friends_domains = []
    for key in request.POST:
        if 'friend_' in key:
            friends_domains.append(request.POST[key])

    info['friends'] = str(friends_domains)

    groups_screen_names = []
    for key in request.POST:
        if 'group_' in key:
            groups_screen_names.append(request.POST[key])

    info['groups'] = str(groups_screen_names)
    return render(request, 'vksearch/add_philter/getName.html', info)


def add_new_filter(request):
    filter_name = request.POST['filter_name']

    filter = {
        'name': filter_name,
        'country_id': int(request.POST['country_id']),
        'cities': list(request.POST['cities']),
        'universities': list(request.POST['universities']),
        'friends': list(request.POST['friends']),
        'groups': list(request.POST['groups'])
    }

    config = json.load(open(CONFIG_FILE, 'r'))
    mdb = VKSearchFilterMongoDB(host=config['mdb_host'], port=config['mdb_port'])
    mdb.load_philter(filter)

    info = {
        'filter_name': filter_name
    }
    return render(request, 'vksearch/add_philter/getNewFilter.html', info)
