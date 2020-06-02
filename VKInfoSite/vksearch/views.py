# pylint: disable=unused-argument, no-self-use, too-many-locals, too-many-branches, too-many-statements
"""VK Search app backend"""
import ast
import json
import time
import vk
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views import View
from main import mongo
from main.decorators import unauthenticated_user, post_method, check_token
from .mongo import VKSearchFiltersStorage
from .vk_scripts import vk_api, VKSearchScripts


@unauthenticated_user
def get_search_params(request):
    """
    'search/' page view - displays page with search arguments
    """
    storage = VKSearchFiltersStorage.connect(db=mongo.get_conn())
    context = {
        'title': 'Search | VK Tracker',
        'filters': storage.get_all_philters_names()
    }
    return render(request, 'vksearch/searchPage.html', context)


class SearchView(View):
    """Search result page view"""

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
        """
        Parse response dict with multiple
        search results into one dict

        :param response: dict with multiple search results
        :return: merged dict with all search results
        """
        result = {
            'count': 0,
            'items': []
        }
        for item in response:
            result['count'] += item['count']
            result['items'] += item['items']
        return result

    def get(self, request):
        """Get method - redirects ro '/search' page"""
        return redirect('/search')

    @method_decorator(check_token, unauthenticated_user)
    def post(self, request):
        """Post method - loads users and displays results"""
        if 'groups_selected' not in request.POST \
                and 'cities_selected' not in request.POST \
                and 'universities_selected' not in request.POST \
                and 'friends_selected' not in request.POST:
            context = {
                'title': 'Error | VK Tracker',
                'message_title': 'Error',
                'message': 'You must specify at least 1 search parameter'
            }
            return render(request, 'info.html', context)

        filter_name = request.POST['filter']
        count = 1000

        storage = VKSearchFiltersStorage.connect(db=mongo.get_conn())
        search_filter = storage.get_filter(filter_name)

        kwargs = {
            'q': '"' + request.POST['q'] + '"' if request.POST['q'] else '""',
            'sex': request.POST['sex'],
            'age_from': request.POST['age_from'],
            'age_to': request.POST['age_to'],
            'has_photo': 1 if 'has_photo' in request.POST else 0,
            'count': count,
            'country_id': search_filter['country_id']
        }

        cities_selected = request.POST.get('cities_selected')
        universities_selected = request.POST.get('universities_selected')
        groups_selected = request.POST.get('groups_selected')
        friends_selected = request.POST.get('friends_selected')

        if cities_selected:
            kwargs['cities'] = search_filter['cities_titles']
        if universities_selected:
            kwargs['universities'] = search_filter['universities']
        if groups_selected:
            kwargs['groups'] = search_filter['groups']

        result = []
        if groups_selected and cities_selected and universities_selected:
            response = []
            kwargs.pop('groups')
            for group_id in search_filter['groups']:
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

            if groups_selected or cities_selected or universities_selected:
                response = vk_api(request, 'execute', code=code)
                time.sleep(0.34)
                result.append(SearchView.parse_response(response))

        if friends_selected:
            code = self.search_by_friends.format(friends=search_filter['friends'])
            result += vk_api(request, 'execute', code=code)

        result_ids = []
        for search_res in result:
            ids = {person['id'] for person in search_res['items']}
            result_ids.append(ids)

        if not result_ids:
            context = {
                'title': 'Error | VK Tracker',
                'message_title': 'Error',
                'message': '0 persons were found.'
            }
            return render(request, 'info.html', context)

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
        context = {
            'title': self.title,
            'count': len(persons),
            'persons': persons,
        }
        return render(request, self.template_name, context)


@check_token
@unauthenticated_user
def add_search_filter_1(request):
    """
    'add_filter/1/' page view - displays page with params of new search filter:
     - Country
     - Cities
     - Universities parameters
    """
    kwargs = {
        'need_all': 1,
        'count': 1000
    }
    countries = vk_api(request, 'database.getCountries', **kwargs)
    context = {
        'title': 'Add search filter | VK Tracker',
        'countries': [item for item in countries['items'] if item['id'] < 5]
    }
    return render(request, 'vksearch/addFilter1.html', context)


@post_method
@unauthenticated_user
def add_search_filter_2(request):
    """
    'add_filter/2/' page view - displays page with params of new search filter:
     - Filter name
     - Universities names
     - Friends
     - Groups
    """
    country_id = request.POST['country_id']
    cities_ids, un_cities_ids, cities_titles = [], [], []
    for key in request.POST:
        if key.startswith('city'):
            req = vk_api(request,
                         method='database.getCities',
                         q=request.POST[key],
                         country_id=country_id)
            if req['count'] == 0:
                country = vk_api(request,
                                 method='database.getCountriesById',
                                 country_ids=country_id)[0]['title']
                context = {
                    'title': 'Error | VK Tracker',
                    'message_title': 'Error',
                    'message': "City '%s' not found in %s." % (request.POST[key], country)
                }
                return render(request, 'info.html', context)
            cities_ids.append(req['items'][0]['id'])
            cities_titles.append(request.POST[key])
        if key.startswith('un_city'):
            req = vk_api(request,
                         method='database.getCities',
                         q=request.POST[key],
                         country_id=country_id)
            if req['count'] == 0:
                country = vk_api(request,
                                 method='database.getCountriesById',
                                 country_ids=country_id)[0]['title']
                context = {
                    'title': 'Error | VK Tracker',
                    'message_title': 'Error',
                    'message': "City '%s' not found in %s." % (request.POST[key], country)
                }
                return render(request, 'info.html', context)
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
            universities += search_by_q['items']
    if not universities and un_filter:
        context = {
            'title': 'Error | VK Tracker',
            'message_title': 'Error',
            'message': 'Universities not found.'
        }
        return render(request, 'info.html', context)
    context = {
        'title': 'Add search filter | VK Tracker',
        'universities': json.dumps(universities),
        'country_id': country_id,
        'cities_ids': cities_ids,
        'cities_titles': cities_titles
    }
    return render(request, 'vksearch/addFilter2.html', context)


@post_method
@unauthenticated_user
def add_filter_result(request):
    """
    'add_filter/result/' page view - displays
    result of adding new search filter
    """
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
                context = {
                    'title': 'Error | VK Tracker',
                    'message_title': 'Error',
                    'message': "User with domain '%s' not found." % request.POST[key]
                }
                return render(request, 'info.html', context)
            if friend['is_closed']:
                context = {
                    'title': 'Error | VK Tracker',
                    'message_title': 'Error',
                    'message': "User account with domain '%s' is closed." % request.POST[key]
                }
                return render(request, 'info.html', context)
            time.sleep(0.34)
            friends_ids.append(friend['id'])

    groups_ids = []
    for key in request.POST:
        if 'group_' in key:
            try:
                _id = vk_api(request, 'groups.getById', group_id=request.POST[key])[0]['id']
            except vk.api.VkAPIError:
                context = {
                    'title': 'Error | VK Tracker',
                    'message_title': 'Error',
                    'message': "Group with screen name '%s' not found." % request.POST[key]
                }
                return render(request, 'info.html', context)
            time.sleep(0.34)
            groups_ids.append(_id)
    new_filter = {
        'name':          filter_name,
        'country_id':    country_id,
        'cities':        ast.literal_eval(cities_ids),
        'cities_titles': cities_titles,
        'universities':  universities_ids,
        'friends':       friends_ids,
        'groups':        groups_ids
    }
    storage = VKSearchFiltersStorage.connect(db=mongo.get_conn())
    storage.add_filter(new_filter)
    context = {
        'title': 'Add search filter | VK Tracker',
        'message_title': 'Adding result',
        'message': f"Filter '{filter_name}' was successfully added to base."
    }
    return render(request, 'info.html', context)


@unauthenticated_user
def delete_filter(request):
    """
    'delete_filter/' page view - displays
    selector with all search filters
    """
    storage = VKSearchFiltersStorage.connect(db=mongo.get_conn())
    context = {
        'title': 'Delete search filter | VK Tracker',
        'filters': storage.get_all_philters_names()
    }
    return render(request, 'vksearch/deleteFilter.html', context)


@post_method
@unauthenticated_user
def delete_filter_result(request):
    """
    'delete_filter/result/' page view - displays
    result of deleting search filter
    """
    filter_name = request.POST['filter']
    storage = VKSearchFiltersStorage.connect(db=mongo.get_conn())
    storage.delete_philter(filter_name)
    context = {
        'title': 'Delete search filter | VK Tracker',
        'message_title': 'Deleting result',
        'message': f"Filter '{filter_name}' was successfully deleted."
    }
    return render(request, 'info.html', context)
