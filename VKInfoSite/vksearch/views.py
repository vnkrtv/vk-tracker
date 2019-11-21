import traceback
import ast

from django.shortcuts import render
from requests.exceptions import ConnectionError
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

    def get_result_for_groups(result):
        new_result = []
        for group_res_search in result:
            new_result.append({
                'count': 0,
                'items': []
            })
            for i in range(len(group_res_search)):
                new_result[-1]['count'] += group_res_search[i]['count']
                new_result[-1]['items'] += group_res_search[i]['items']
        return new_result

    def get_result(result):
        new_result = [{
            'count': 0,
            'items': []
        }]
        for i in range(len(result)):
            new_result[-1]['count'] += result[i]['count']
            new_result[-1]['items'] += result[i]['items']
        return new_result

    if 'groups_selected' not in request.POST\
            and 'cities_selected' not in request.POST \
            and 'universities_selected' not in request.POST\
            and 'friends_selected' not in request.POST:
        info = {
            'error': 'you must specify at least 1 search parameter'
        }
        return render(request, 'vksearch/error.html', info)

    filter_name = request.POST['filter']
    count = 1000

    with open(CONFIG_FILE, 'r') as file:
        config = json.load(file)
    mdb = VKSearchFilterMongoDB(host=config['mdb_host'], port=config['mdb_port'])
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
                                                   "hometown": "cities[t]",
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
            sleep(0.34)
            result.append(vk_api('execute', code=search_by_universities_and_cities))
        result = get_result_for_groups(result)

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
        sleep(0.34)
        result += vk_api('execute', code=search_by_universities_and_cities)
        result = get_result(result)

    if 'groups_selected' in request.POST\
            and 'cities_selected' in request.POST\
            and 'universities_selected' not in request.POST:
        for group_id in filter['groups']:
            kwargs['group_id'] = group_id
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
                                                "group_id": {group_id},
                                                "fields": "photo_400_orig,domain,relation,sex"      
                                            }});
                        res.push(users);
                        i = i + 1;
                    }}
                    return res;
            """.format(**kwargs).replace('\n', '').replace('  ', '')
            sleep(0.34)
            result.append(vk_api('execute', code=search_by_cities))
        result = get_result_for_groups(result)

    if 'groups_selected' in request.POST\
            and 'cities_selected' not in request.POST\
            and 'universities_selected' in request.POST:
        for group_id in filter['groups']:
            kwargs['group_id'] = group_id
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
                                                "group_id": {group_id},
                                                "fields": "photo_400_orig,domain,relation,sex"      
                                            }});
                        res.push(users);
                        i = i + 1;
                    }}
                    return res;
            """.format(**kwargs).replace('\n', '').replace('  ', '')
            sleep(0.34)
            result.append(vk_api('execute', code=search_by_universities))
        result = get_result_for_groups(result)

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
        sleep(0.34)
        result += vk_api('execute', code=search_by_groups)

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
                                            "sex": {sex},
                                            "age_from": {age_from},
                                            "age_to": {age_to},
                                            "has_photo": {has_photo},
                                            "hometown": cities[i],
                                            "fields": "photo_400_orig,domain,relation,sex"      
                                        }});
                    res.push(users);
                    i = i + 1;
                }}
                return res;
        """.format(**kwargs).replace('\n', '').replace('  ', '')
        sleep(0.34)
        result += vk_api('execute', code=search_by_cities)
        result = get_result(result)

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
                                            "age_from": {age_from},
                                            "age_to": {age_to},
                                            "has_photo": {has_photo},
                                            "university": universities[i],
                                            "fields": "photo_400_orig,domain,relation,sex"      
                                        }});
                    res.push(users);
                    i = i + 1;
                }}
                return res;
        """.format(**kwargs).replace('\n', '').replace('  ', '')
        sleep(0.34)

        result += vk_api('execute', code=search_by_universities)
        result = get_result(result)

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
        ids = set()
        for person in search_res['items']:
            ids.add(person['id'])
        result_ids.append(ids)

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
    info['result'] = json.dumps(result, indent=2)
    info['result_ids'] = [len(item) for item in result_ids]
    info['unique_ids'] = unique_ids
    info['request'] = request.POST
    info['filter'] = filter
    info['res_len'] = len(result)
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


def get_new_filter_cities(request):
    country_id = request.POST['country']
    cities_num = int(request.POST['cities_num'])
    un_cities_num = int(request.POST['un_cities_num'])

    info = {
        'cities_num': list(range(cities_num)),
        'un_cities_num': list(range(un_cities_num)),
        'country_id': country_id,
    }
    return render(request, 'vksearch/add_filter/getCities.html', info)


def get_new_filter_universities(request):
    country_id = request.POST['country_id']
    cities = []
    cities_titles = []
    for key in request.POST:
        if key.startswith('city'):
            req = vk_api('database.getCities', q=request.POST[key], country_id=country_id)
            if req['count'] == 0:
                info = {
                    'error': 'city %s not found.' % request.POST[key]
                }
                return render(request, 'vksearch/error.html', info)
            cities.append(req['items'][0]['id'])
            cities_titles.append(request.POST[key])

    un_cities = []
    for key in request.POST:
        if key.startswith('un_city'):
            req = vk_api('database.getCities', q=request.POST[key], country_id=country_id)
            if req['count'] == 0:
                info = {
                    'error': 'city %s not found.' % request.POST[key]
                }
                return render(request, 'vksearch/error.html', info)
            un_cities.append(req['items'][0]['id'])

    info = {
        'cities': str(cities),
        'cities_titles': str(cities_titles),
        'country_id': country_id,
    }

    if 'university_set' in request.POST:
        info['university_set'] = 1
        info['universities_num'] = range(int(request.POST['universities_num']))
    else:
        info['university_set'] = 0

    universities = []
    for city in un_cities:
        kwargs = {
            'universities_filter': request.POST['universities_filter'].split(','),
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
        for search_by_q in req:
            universities += [item for item in search_by_q['items']]

    if not universities:
        info = {
            'error': 'no universities found.'
        }
        return render(request, 'vksearch/error.html', info)

    info['universities'] = universities
    return render(request, 'vksearch/add_filter/getUniversities.html', info)


def get_new_filter_friends_and_groups(request):
    print(request.POST)
    info = {
        'country_id': request.POST['country_id'],
        'cities': request.POST['cities'],
        'cities_titles': request.POST['cities_titles']
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
        'cities_titles': request.POST['cities_titles'],
        'universities': request.POST['universities']
    }
    friends_ids = []
    for key in request.POST:
        if 'friend_' in key:
            try:
                friend = vk_api('users.get', user_ids=request.POST[key])[0]
            except vk.api.VkAPIError:
                info = {
                    'error': 'user with domain %s not found.' % request.POST[key]
                }
                return render(request, 'vksearch/error.html', info)
            if friend['is_closed']:
                info = {
                    'error': 'user account with domain %s is closed.' % request.POST[key]
                }
                return render(request, 'vksearch/error.html', info)
            sleep(0.34)
            friends_ids.append(friend['id'])

    info['friends'] = str(friends_ids)

    groups_screen_names = []
    for key in request.POST:
        if 'group_' in key:
            try:
                id = vk_api('groups.getById', group_id=request.POST[key])[0]['id']
            except vk.api.VkAPIError:
                info = {
                    'error': 'group with screen name %s not found.' % request.POST[key]
                }
                return render(request, 'vksearch/error.html', info)
            sleep(0.34)
            groups_screen_names.append(id)

    info['groups'] = str(groups_screen_names)
    return render(request, 'vksearch/add_filter/getName.html', info)


def add_new_filter(request):
    filter_name = request.POST['filter_name']

    filter = {
        'name':          filter_name,
        'country_id':    int(request.POST['country_id']),
        'cities':        ast.literal_eval(request.POST['cities']),
        'cities_titles': ast.literal_eval(request.POST['cities_titles']),
        'universities':  ast.literal_eval(request.POST['universities']) if request.POST['universities'] else [],
        'friends':       ast.literal_eval(request.POST['friends'])      if request.POST['friends']      else [],
        'groups':        ast.literal_eval(request.POST['groups'])       if request.POST['groups']       else []
    }

    with open(CONFIG_FILE, 'r') as file:
        config = json.load(file)
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

