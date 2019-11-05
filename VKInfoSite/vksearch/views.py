import traceback
import json
import ast

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
    with open(CONFIG_FILE, 'r') as file:
        config = json.load(file)
    mdb = VKSearchFilterMongoDB(host=config['mdb_host'], port=config['mdb_port'])
    info = {
        'filters': mdb.get_all_philters_names()
    }
    return render(request, 'vksearch/search/searchPage.html', info)


def get_search_result(request):
    filter_name = request.POST['filter']
    count = 100

    with open(CONFIG_FILE, 'r') as file:
        config = json.load(file)
    mdb = VKSearchFilterMongoDB(host=config['mdb_host'], port=config['mdb_port'])
    filter = mdb.get_filter(filter_name)

    kwargs = {
        'q': request.POST['q'] if request.POST['q'] else '""',
        'sex': request.POST['sex'],
        'age_from': request.POST['age_from'],
        'age_to': request.POST['age_to'],
        'has_photo': 1 if 'has_photo' in request.POST else 0,
        'count': count,
        'universities': filter['universities'],
        'cities': filter['cities'],
        'country_id': filter['country_id']
    }

    result = []
    for group_id in filter['groups']:
        kwargs['group_id'] = group_id
        search_by_universities_and_groups = """
                var universities = {universities};
                var cities = {cities};
                var res = [];
                var i = 0;

                while (i < universities.length) {{
                    var t = 0;
                    while (t < cities.length) {{
                        var users = API.users.search({{
                                               "q": {q},
                                               "count": {count},
                                               "country": {country_id},
                                               "city": cities[t],
                                               "university": universities[i],
                                               "sex": {sex},
                                               "age_from": {age_from},
                                               "age_to": {age_to},
                                               "has_photo": {has_photo},
                                               "group_id": {group_id},
                                               "fields": "photo_200_orig"      
                                               }});
                        res.push(users);
                        t = t + 1;
                    }}
                    i = i + 1;
                }}
                return res;
        """.format(**kwargs).replace('\n', '').replace('  ', '')

        result.append(vk_api('execute', code=search_by_universities_and_groups)[0])

    groups_ids = []
    result = [item['items'] for item in result]
    res = []
    for item in result:
        res += item

    info = {
        'result': res
    }
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
    return render(request, 'vksearch/add_filter/getCountry.html', info)


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
    return render(request, 'vksearch/add_filter/getRegion.html', info)


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
    return render(request, 'vksearch/add_filter/getCities.html', info)


def get_new_filter_universities(request):
    cities = []
    for key in request.POST:
        if key.startswith('city'):
            cities.append(int(request.POST[key]))

    un_cities = []
    for key in request.POST:
        if key.startswith('un_city'):
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
    return render(request, 'vksearch/add_filter/getUniversities.html', info)


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
    return render(request, 'vksearch/add_filter/getGroupsAndFriends.html', info)


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
            id = vk_api('groups.getById', group_id=request.POST[key])[0]['id']
            sleep(0.34)
            groups_screen_names.append(id)

    info['groups'] = str(groups_screen_names)
    return render(request, 'vksearch/add_filter/getName.html', info)


def add_new_filter(request):
    filter_name = request.POST['filter_name']

    filter = {
        'name':         filter_name,
        'country_id':   int(request.POST['country_id']),
        'cities':       ast.literal_eval(request.POST['cities']),
        'universities': ast.literal_eval(request.POST['universities']) if request.POST['universities'] else [],
        'friends':      ast.literal_eval(request.POST['friends'])      if request.POST['friends']      else [],
        'groups':       ast.literal_eval(request.POST['groups'])       if request.POST['groups']       else []
    }

    config = json.load(open(CONFIG_FILE, 'r'))
    mdb = VKSearchFilterMongoDB(host=config['mdb_host'], port=config['mdb_port'])
    mdb.load_philter(filter)

    info = {
        'filter_name': filter_name
    }
    return render(request, 'vksearch/add_filter/getNewFilter.html', info)


def delete_filter(request):
    with open(CONFIG_FILE, 'r') as file:
        config = json.load(file)
    mdb = VKSearchFilterMongoDB(host=config['mdb_host'], port=config['mdb_port'])
    info = {
        'filters': mdb.get_all_philters_names()
    }
    return render(request, 'vksearch/delete_filter/getName.html', info)


def delete_filter_result(request):
    filter_name = request.POST['filter']

    with open(CONFIG_FILE, 'r') as file:
        config = json.load(file)
    mdb = VKSearchFilterMongoDB(host=config['mdb_host'], port=config['mdb_port'])
    mdb.delete_philter(filter_name)

    info = {
        'filter_name': request.POST['filter']
    }
    return render(request, 'vksearch/delete_filter/deleteResult.html', info)

