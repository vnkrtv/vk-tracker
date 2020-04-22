import ast
import vk
import json
import time
from django.shortcuts import render, redirect
from .mongodb import VKSearchFiltersStorage
from django.conf import settings


def unauthenticated_user(view_func):
    """
    Checked if user is authorized
    """
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_authenticated:
            return view_func(request, *args, **kwargs)
        else:
            return redirect('/')
    return wrapper_func


def vk_api(method, **kwargs):
    with open(settings.CONFIG, 'r') as file:
        token = json.load(file)['vk_token']
    session = vk.API(vk.Session(access_token=token))
    return eval('session.' + method)(v=5.103, **kwargs)


@unauthenticated_user
def get_search_params(request):
    with open(settings.CONFIG, 'r') as file:
        config = json.load(file)
    mdb = VKSearchFiltersStorage.connect_to_mongodb(
        host=config['mdb_host'],
        port=config['mdb_port'],
        db_name=config['mdb_dbname']
    )
    info = {
        'filters': mdb.get_all_philters_names()
    }
    return render(request, 'vksearch/searchPage.html', info)


@unauthenticated_user
def get_search_result(request):

    def parse_response(response):
        result = {
            'count': 0,
            'items': []
        }
        for item in response:
            result['count'] += item['count']
            result['items'] += item['items']
        return result

    if 'groups_selected' not in request.POST\
            and 'cities_selected' not in request.POST \
            and 'universities_selected' not in request.POST\
            and 'friends_selected' not in request.POST:
        info = {
            'title': 'Error',
            'message': 'You must specify at least 1 search parameter'
        }
        return render(request, 'info.html', info)

    filter_name = request.POST['filter']
    count = 1000

    with open(settings.CONFIG, 'r') as file:
        config = json.load(file)
    mdb = VKSearchFiltersStorage.connect_to_mongodb(
        host=config['mdb_host'],
        port=config['mdb_port'],
        db_name=config['mdb_dbname']
    )
    filter = mdb.get_filter(filter_name)

    kwargs = {
        'q': '"' + request.POST['q'] + '"' if request.POST['q'] else '""',
        'sex': request.POST['sex'],
        'age_from': request.POST['age_from'],
        'age_to': request.POST['age_to'],
        'has_photo': 1 if 'has_photo' in request.POST else 0,
        'count': count,
        'country_id': filter['country_id']
    }
    if 'cities_selected' in request.POST:
        kwargs['cities'] = filter['cities_titles']
    if 'universities_selected' in request.POST:
        kwargs['universities'] = filter['universities']

    result = []
    if 'groups_selected' in request.POST\
            and 'cities_selected' in request.POST\
            and 'universities_selected' in request.POST:
        response = []
        for group_id in filter['groups']:
            kwargs['group_id'] = group_id
            search_by_universities_and_cities = """
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
                                                   "hometown": cities[t],
                                                   "university": universities[i],
                                                   "sex": {sex},
                                                   "age_from": {age_from},
                                                   "age_to": {age_to},
                                                   "has_photo": {has_photo},
                                                   "group_id": {group_id},
                                                   "fields": "photo_400_orig,domain,relation,sex"      
                                                   }});
                            res.push(users);
                            t = t + 1;
                        }}
                        i = i + 1;
                    }}
                    return res;
            """.format(**kwargs).replace('\n', '').replace('  ', '')
            response += vk_api('execute', code=search_by_universities_and_cities)
            time.sleep(0.34)
        result.append(parse_response(response))

    if 'groups_selected' not in request.POST\
            and 'cities_selected' in request.POST\
            and 'universities_selected' in request.POST:
        search_by_universities_and_cities = """
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
                                               "hometown": cities[t],
                                               "university": universities[i],
                                               "sex": {sex},
                                               "age_from": {age_from},
                                               "age_to": {age_to},
                                               "has_photo": {has_photo},
                                               "fields": "photo_400_orig,domain,relation,sex"      
                                               }});
                        res.push(users);
                        t = t + 1;
                    }}
                    i = i + 1;
                }}
                return res;
        """.format(**kwargs).replace('\n', '').replace('  ', '')
        response = vk_api('execute', code=search_by_universities_and_cities)
        time.sleep(0.34)
        result.append(parse_response(response))

    if 'groups_selected' not in request.POST \
            and 'cities_selected' in request.POST \
            and 'universities_selected' not in request.POST:
        search_by_cities = """
                            var cities = {cities};
                            var res = [];
                            var i = 0;

                            while (i < cities.length) {{
                                var users = API.users.search({{
                                                        "q": {q},
                                                        "count": {count},
                                                        "country": {country_id},
                                                        "hometown": cities[i],
                                                        "sex": {sex},
                                                        "age_from": {age_from},
                                                        "age_to": {age_to},
                                                        "has_photo": {has_photo},
                                                        "fields": "photo_400_orig,domain,relation,sex"      
                                                    }});
                                res.push(users);
                                i = i + 1;
                            }}
                            return res;
                    """.format(**kwargs).replace('\n', '').replace('  ', '')
        response = vk_api('execute', code=search_by_cities)
        time.sleep(0.34)
        result.append(parse_response(response))

    if 'groups_selected' not in request.POST \
            and 'cities_selected' not in request.POST \
            and 'universities_selected' in request.POST:
        search_by_universities = """
                            var universities = {universities};
                            var res = [];
                            var i = 0;

                            while (i < universities.length) {{
                                var users = API.users.search({{
                                                        "q": {q},
                                                        "count": {count},
                                                        "country": {country_id},
                                                        "sex": {sex},
                                                        "university": universities[i],
                                                        "age_from": {age_from},
                                                        "age_to": {age_to},
                                                        "has_photo": {has_photo},
                                                        "fields": "photo_400_orig,domain,relation,sex"      
                                                    }});
                                res.push(users);
                                i = i + 1;
                            }}
                            return res;
                    """.format(**kwargs).replace('\n', '').replace('  ', '')
        response = vk_api('execute', code=search_by_universities)
        time.sleep(0.34)
        result.append(parse_response(response))

    if 'groups_selected' in request.POST\
            and 'cities_selected' in request.POST\
            and 'universities_selected' not in request.POST:
        kwargs['groups'] = filter['groups']
        search_by_groups_and_cities = """
                var groups = {groups};
                var cities = {cities};
                var res = [];
                var i = 0;

                while (i < groups.length) {{
                    var t = 0;
                    while (t < cities.length) {{
                        var users = API.users.search({{
                                               "q": {q},
                                               "count": {count},
                                               "country": {country_id},
                                               "hometown": cities[t],
                                               "group_id": groups[i],
                                               "sex": {sex},
                                               "age_from": {age_from},
                                               "age_to": {age_to},
                                               "has_photo": {has_photo},
                                               "fields": "photo_400_orig,domain,relation,sex"      
                                               }});
                        res.push(users);
                        t = t + 1;
                    }}
                    i = i + 1;
                }}
                return res;
        """.format(**kwargs).replace('\n', '').replace('  ', '')
        response = vk_api('execute', code=search_by_groups_and_cities)
        time.sleep(0.34)
        result.append(parse_response(response))

    if 'groups_selected' in request.POST\
            and 'cities_selected' not in request.POST\
            and 'universities_selected' in request.POST:
        kwargs['groups'] = filter['groups']
        search_by_groups_and_universities = """
                var groups = {groups};
                var universities = {universities};
                var res = [];
                var i = 0;

                while (i < groups.length) {{
                    var t = 0;
                    while (t < universities.length) {{
                        var users = API.users.search({{
                                               "q": {q},
                                               "count": {count},
                                               "country": {country_id},
                                               "university": universities[t],
                                               "group_id": groups[i],
                                               "sex": {sex},
                                               "age_from": {age_from},
                                               "age_to": {age_to},
                                               "has_photo": {has_photo},
                                               "fields": "photo_400_orig,domain,relation,sex"      
                                               }});
                        res.push(users);
                        t = t + 1;
                    }}
                    i = i + 1;
                }}
                return res;
        """.format(**kwargs).replace('\n', '').replace('  ', '')
        response = vk_api('execute', code=search_by_groups_and_universities)
        time.sleep(0.34)
        result.append(parse_response(response))

    if 'groups_selected' in request.POST\
            and 'cities_selected' not in request.POST\
            and 'universities_selected' not in request.POST:
        kwargs['groups'] = filter['groups']
        search_by_groups = """
                var groups = {groups};
                var res = [];
                var i = 0;

                while (i < groups.length) {{
                    var users = API.users.search({{
                                            "q": {q},
                                            "count": {count},
                                            "country": {country_id},
                                            "sex": {sex},
                                            "age_from": {age_from},
                                            "age_to": {age_to},
                                            "has_photo": {has_photo},
                                            "group_id": groups[i],
                                            "fields": "photo_400_orig,domain,relation,sex"      
                                        }});
                    res.push(users);
                    i = i + 1;
                }}
                return res;
        """.format(**kwargs).replace('\n', '').replace('  ', '')
        time.sleep(0.34)
        response = vk_api('execute', code=search_by_groups)
        result.append(parse_response(response))

    if 'friends_selected' in request.POST:
        search_by_friends = """
                var friends = {friends};
                var res = [];
                var i = 0;

                while (i < friends.length) {{
                    var users = API.friends.get({{
                                           "user_id": friends[i],
                                           "fields": "photo_400_orig,domain,relation,sex"      
                                           }});
                    res.push(users);
                    i = i + 1;
                }}
                return res;
        """.format(friends=filter['friends']).replace('\n', '').replace('  ', '')
        result += vk_api('execute', code=search_by_friends)

    result_ids = []
    for search_res in result:
        ids = {person['id'] for person in search_res['items']}
        result_ids.append(ids)

    if not result_ids:
        info = {
            'title': 'Error',
            'message': '0 persons were found.'
        }
        return render(request, 'info.html', info)

    unique_ids = result_ids[0].copy()
    for ids in result_ids:
        unique_ids &= ids

    relation_options = {
        1: 'not married',               # не женат/не замужем
        2: 'has boyfriend/girlfriend',  # есть друг/есть подруга',
        3: 'engaged',                   # 'помолвлен/помолвлена',
        4: 'married',                   # 'женат/замужем',
        5: 'it\'s complicated',         # 'всё сложно',
        6: 'actively looking',          # 'в активном поиске',
        7: 'in love',                   # 'влюблён/влюблена',
        8: 'in a civil marriage',       # 'в гражданском браке',
        0: 'not indicated',             # 'не указано'
    }

    persons = []
    for search_res in result:
        for person in search_res['items']:
            fullname = person['first_name'] + ' ' + person['last_name']
            if person['id'] in unique_ids and kwargs['q'][1:-1] in fullname:
                if person['sex'] == int(kwargs['sex']) or int(kwargs['sex']) == 0:
                    if 'relation' in person:
                        person['relation'] = relation_options[person['relation']]
                    else:
                        person['relation'] = relation_options[0]
                    persons.append(person)
                    unique_ids.remove(person['id'])

    info = {
        'count': len(persons),
        'persons': persons,
    }
    return render(request, 'vksearch/searchResultPage.html', info)


@unauthenticated_user
def add_search_filter(request):
    kwargs = {
        'need_all': 1,
        'count': 1000
    }
    countries = vk_api('database.getCountries', **kwargs)
    info = {
        'countries': [item for item in countries['items'] if item['id'] < 5]
    }
    return render(request, 'vksearch/addFilter1.html', info)


@unauthenticated_user
def get_new_filter_2(request):
    country_id = request.POST['country_id']
    cities_ids, un_cities_ids, cities_titles = [], [], []
    for key in request.POST:
        if key.startswith('city'):
            req = vk_api('database.getCities', q=request.POST[key], country_id=country_id)
            if req['count'] == 0:
                country = vk_api('database.getCountriesById', country_ids=country_id)[0]['title']
                info = {
                    'title': 'Error',
                    'message': "City '%s' not found in %s." % (request.POST[key], country)
                }
                return render(request, 'info.html', info)
            cities_ids.append(req['items'][0]['id'])
            cities_titles.append(request.POST[key])
        if key.startswith('un_city'):
            req = vk_api('database.getCities', q=request.POST[key], country_id=country_id)
            if req['count'] == 0:
                info = {
                    'title': 'Error',
                    'message': "City '%s' not found." % request.POST[key]
                }
                return render(request, 'info.html', info)
            un_cities_ids.append(req['items'][0]['id'])

    un_filter = request.POST['universities_filter']
    universities = []
    for city in un_cities_ids:
        kwargs = {
            'universities_filter': un_filter.split(','),
            'country_id': request.POST['country_id'],
            'city_id': city,
            'count': 1000
        }
        code = """
            var q = {universities_filter};
            var res = [];
            var i = 0;
            
            while (i < q.length) {{
                var users = API.database.getUniversities({{
                                        "q": q[i],
                                        "country_id": {country_id},
                                        "city_id": {city_id},
                                        "count": {count}                                              
                                    }});
                res.push(users);
                i = i + 1;
            }}
            return res;
        """.format(**kwargs).replace('\n', '').replace('  ', '')
        req = vk_api('execute', code=code)
        time.sleep(0.35)
        for search_by_q in req:
            universities += [item for item in search_by_q['items']]
    if not universities and un_filter:
        info = {
            'title': 'Error',
            'message': 'Universities not found.'
        }
        return render(request, 'info.html', info)
    info = {
        'universities': universities,
        'country_id': country_id,
        'cities_ids': cities_ids,
        'cities_titles': cities_titles
    }
    return render(request, 'vksearch/addFilter2.html', info)


@unauthenticated_user
def add_filter_result(request):
    country_id = int(request.POST['country_id'])
    cities_ids = request.POST['cities_ids']
    cities_titles = request.POST['cities_titles']
    filter_name = request.POST['filter_name']

    universities_ids = []
    for key in request.POST:
        if 'university_' in key:
            universities_ids.append(int(request.POST[key]))

    friends_ids = []
    for key in request.POST:
        if 'friend_' in key:
            try:
                friend = vk_api('users.get', user_ids=request.POST[key])[0]
            except vk.api.VkAPIError:
                info = {
                    'title': 'Error',
                    'message': "User with domain '%s' not found." % request.POST[key]
                }
                return render(request, 'info.html', info)
            if friend['is_closed']:
                info = {
                    'title': 'Error',
                    'message': "User account with domain '%s' is closed." % request.POST[key]
                }
                return render(request, 'info.html', info)
            time.sleep(0.34)
            friends_ids.append(friend['id'])

    groups_ids = []
    for key in request.POST:
        if 'group_' in key:
            try:
                _id = vk_api('groups.getById', group_id=request.POST[key])[0]['id']
            except vk.api.VkAPIError:
                info = {
                    'title': 'Error',
                    'message': "Group with screen name '%s' not found." % request.POST[key]
                }
                return render(request, 'info.html', info)
            time.sleep(0.34)
            groups_ids.append(_id)

    _filter = {
        'name':          filter_name,
        'country_id':    country_id,
        'cities':        ast.literal_eval(cities_ids),
        'cities_titles': cities_titles,
        'universities':  universities_ids,
        'friends':       friends_ids,
        'groups':        groups_ids
    }

    with open(settings.CONFIG, 'r') as file:
        config = json.load(file)
    mdb = VKSearchFiltersStorage.connect_to_mongodb(
        host=config['mdb_host'],
        port=config['mdb_port'],
        db_name=config['mdb_dbname']
    )
    mdb.add_filter(_filter)
    info = {
        'title': 'Adding result',
        'message': f"Filter '{filter_name}' was successfully added to base."
    }
    return render(request, 'info.html', info)


@unauthenticated_user
def delete_filter(request):
    with open(settings.CONFIG, 'r') as file:
        config = json.load(file)
    mdb = VKSearchFiltersStorage.connect_to_mongodb(
        host=config['mdb_host'],
        port=config['mdb_port'],
        db_name=config['mdb_dbname']
    )
    info = {
        'filters': mdb.get_all_philters_names()
    }
    return render(request, 'vksearch/deleteFilter.html', info)


@unauthenticated_user
def delete_filter_result(request):
    filter_name = request.POST['filter']
    with open(settings.CONFIG, 'r') as file:
        config = json.load(file)
    mdb = VKSearchFiltersStorage.connect_to_mongodb(
        host=config['mdb_host'],
        port=config['mdb_port'],
        db_name=config['mdb_dbname']
    )
    mdb.delete_philter(filter_name)
    info = {
        'title': 'Deleting result',
        'message': f"Filter '{filter_name}' was successfully deleted."
    }
    return render(request, 'info.html', info)
