import ast
import vk
import time
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views import View
from main import mongo
from main.decorators import unauthenticated_user, post_method, check_token
from .mongo import VKSearchFiltersStorage
from .vkscripts import vk_api, VKSearchScripts


@unauthenticated_user
def get_search_params(request):
    storage = VKSearchFiltersStorage.connect(db=mongo.get_conn())
    info = {
        'title': 'Search | VK Tracker',
        'filters': storage.get_all_philters_names()
    }
    return render(request, 'vksearch/searchPage.html', info)


class SearchView(View):
    template_name = 'vksearch/searchResultPage.html'
    title = 'Search results | VK Tracker'
    search_by_groups_cities_universities = VKSearchScripts.by_groups_cities_universities
    search_by_cities_universities = VKSearchScripts.by_cities_universities
    search_by_cities = VKSearchScripts.by_cities
    search_by_universities = VKSearchScripts.by_universities
    search_by_groups_cities = VKSearchScripts.by_groups_cities
    search_by_groups_universities = VKSearchScripts.by_groups_universities
    search_by_groups = VKSearchScripts.by_groups
    search_by_friends = VKSearchScripts.by_friends
    relation_options = {
        1: 'not married',  # не женат/не замужем
        2: 'has boyfriend/girlfriend',  # есть друг/есть подруга',
        3: 'engaged',  # 'помолвлен/помолвлена',
        4: 'married',  # 'женат/замужем',
        5: 'it\'s complicated',  # 'всё сложно',
        6: 'actively looking',  # 'в активном поиске',
        7: 'in love',  # 'влюблён/влюблена',
        8: 'in a civil marriage',  # 'в гражданском браке',
        0: 'not indicated',  # 'не указано'
    }

    @staticmethod
    def parse_response(response):
        result = {
            'count': 0,
            'items': []
        }
        for item in response:
            result['count'] += item['count']
            result['items'] += item['items']
        return result

    def get(self, request):
        return redirect('/search')

    @method_decorator(check_token, unauthenticated_user)
    def post(self, request):
        if 'groups_selected' not in request.POST \
                and 'cities_selected' not in request.POST \
                and 'universities_selected' not in request.POST \
                and 'friends_selected' not in request.POST:
            info = {
                'title': 'Error',
                'message': 'You must specify at least 1 search parameter'
            }
            return render(request, 'info.html', info)

        filter_name = request.POST['filter']
        count = 1000

        storage = VKSearchFiltersStorage.connect(db=mongo.get_conn())
        _filter = storage.get_filter(filter_name)

        kwargs = {
            'q': '"' + request.POST['q'] + '"' if request.POST['q'] else '""',
            'sex': request.POST['sex'],
            'age_from': request.POST['age_from'],
            'age_to': request.POST['age_to'],
            'has_photo': 1 if 'has_photo' in request.POST else 0,
            'count': count,
            'country_id': _filter['country_id']
        }

        cities_selected = request.POST.get('cities_selected')
        universities_selected = request.POST.get('universities_selected')
        groups_selected = request.POST.get('groups_selected')
        friends_selected = request.POST.get('friends_selected')

        if cities_selected:
            kwargs['cities'] = _filter['cities_titles']
        if universities_selected:
            kwargs['universities'] = _filter['universities']
        if groups_selected:
            kwargs['groups'] = _filter['groups']

        result = []
        if groups_selected and cities_selected and universities_selected:
            response = []
            kwargs.pop('groups')
            for group_id in _filter['groups']:
                kwargs['group_id'] = group_id
                code = self.search_by_groups_cities_universities.format(**kwargs)
                response += vk_api(request, 'execute', code=code)
                time.sleep(0.34)
            result.append(SearchView.parse_response(response))
        else:
            if groups_selected and cities_selected:
                code = self.search_by_groups_cities.format(**kwargs)

            if groups_selected and universities_selected:
                code = self.search_by_groups_universities.format(**kwargs)

            if cities_selected and universities_selected:
                code = self.search_by_cities_universities.format(**kwargs)

            if groups_selected:
                code = self.search_by_groups.format(**kwargs)

            if cities_selected:
                code = self.search_by_cities.format(**kwargs)

            if universities_selected:
                code = self.search_by_universities.format(**kwargs)

            response = vk_api(request, 'execute', code=code)
            time.sleep(0.34)
            result.append(SearchView.parse_response(response))

        if friends_selected:
            code = self.search_by_friends.format(friends=_filter['friends'])
            result += vk_api(request, 'execute', code=code)

        result_ids = []
        for search_res in result:
            ids = {person['id'] for person in search_res['items']}
            result_ids.append(ids)

        if not result_ids:
            info = {
                'title': 'Error | VK Tracker',
                'message_title': 'Error',
                'message': '0 persons were found.'
            }
            return render(request, 'info.html', info)

        unique_ids = result_ids[0].copy()
        for ids in result_ids:
            unique_ids &= ids

        persons = []
        for search_res in result:
            for person in search_res['items']:
                fullname = person['first_name'] + ' ' + person['last_name']
                if person['id'] in unique_ids and kwargs['q'][1:-1] in fullname:
                    if person['sex'] == int(kwargs['sex']) or int(kwargs['sex']) == 0:
                        if 'relation' in person:
                            person['relation'] = self.relation_options[person['relation']]
                        else:
                            person['relation'] = self.relation_options[0]
                        persons.append(person)
                        unique_ids.remove(person['id'])
        info = {
            'title': self.title,
            'count': len(persons),
            'persons': persons,
        }
        return render(request, self.template_name, info)


@check_token
@unauthenticated_user
def add_search_filter(request):
    kwargs = {
        'title': 'Add search filter | VK Tracker',
        'need_all': 1,
        'count': 1000
    }
    countries = vk_api(request, 'database.getCountries', **kwargs)
    info = {
        'countries': [item for item in countries['items'] if item['id'] < 5]
    }
    return render(request, 'vksearch/addFilter1.html', info)


@post_method
@unauthenticated_user
def get_new_filter_2(request):
    country_id = request.POST['country_id']
    cities_ids, un_cities_ids, cities_titles = [], [], []
    for key in request.POST:
        if key.startswith('city'):
            req = vk_api(request, 'database.getCities', q=request.POST[key], country_id=country_id)
            if req['count'] == 0:
                country = vk_api(request, 'database.getCountriesById', country_ids=country_id)[0]['title']
                info = {
                    'title': 'Error | VK Tracker',
                    'message_title': 'Error',
                    'message': "City '%s' not found in %s." % (request.POST[key], country)
                }
                return render(request, 'info.html', info)
            cities_ids.append(req['items'][0]['id'])
            cities_titles.append(request.POST[key])
        if key.startswith('un_city'):
            req = vk_api(request, 'database.getCities', q=request.POST[key], country_id=country_id)
            if req['count'] == 0:
                info = {
                    'title': 'Error | VK Tracker',
                    'message_title': 'Error',
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
        req = vk_api(request, 'execute', code=code)
        time.sleep(0.35)
        for search_by_q in req:
            universities += [item for item in search_by_q['items']]
    if not universities and un_filter:
        info = {
            'title': 'Error | VK Tracker',
            'message_title': 'Error',
            'message': 'Universities not found.'
        }
        return render(request, 'info.html', info)
    info = {
        'title': 'Add search filter | VK Tracker',
        'universities': universities,
        'country_id': country_id,
        'cities_ids': cities_ids,
        'cities_titles': cities_titles
    }
    return render(request, 'vksearch/addFilter2.html', info)


@post_method
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
                friend = vk_api(request, 'users.get', user_ids=request.POST[key])[0]
            except vk.api.VkAPIError:
                info = {
                    'title': 'Error | VK Tracker',
                    'message_title': 'Error',
                    'message': "User with domain '%s' not found." % request.POST[key]
                }
                return render(request, 'info.html', info)
            if friend['is_closed']:
                info = {
                    'title': 'Error | VK Tracker',
                    'message_title': 'Error',
                    'message': "User account with domain '%s' is closed." % request.POST[key]
                }
                return render(request, 'info.html', info)
            time.sleep(0.34)
            friends_ids.append(friend['id'])

    groups_ids = []
    for key in request.POST:
        if 'group_' in key:
            try:
                _id = vk_api(request, 'groups.getById', group_id=request.POST[key])[0]['id']
            except vk.api.VkAPIError:
                info = {
                    'title': 'Error | VK Tracker',
                    'message_title': 'Error',
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
    storage = VKSearchFiltersStorage.connect(db=mongo.get_conn())
    storage.add_filter(_filter)
    info = {
        'title': 'New search filter was added | VK Tracker',
        'message_title': 'Adding result',
        'message': f"Filter '{filter_name}' was successfully added to base."
    }
    return render(request, 'info.html', info)


@unauthenticated_user
def delete_filter(request):
    storage = VKSearchFiltersStorage.connect(db=mongo.get_conn())
    info = {
        'title': 'Delete search filter | VK Tracker',
        'filters': storage.get_all_philters_names()
    }
    return render(request, 'vksearch/deleteFilter.html', info)


@post_method
@unauthenticated_user
def delete_filter_result(request):
    filter_name = request.POST['filter']
    storage = VKSearchFiltersStorage.connect(db=mongo.get_conn())
    storage.delete_philter(filter_name)
    info = {
        'title': 'Search filter was deleted | VK Tracker',
        'message_title': 'Deleting result',
        'message': f"Filter '{filter_name}' was successfully deleted."
    }
    return render(request, 'info.html', info)
