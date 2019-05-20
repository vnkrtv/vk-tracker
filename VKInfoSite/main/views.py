import traceback
import json

from django.shortcuts import render
from requests.exceptions import ConnectionError
from neobolt.exceptions import ServiceUnavailable
from pymongo.errors import ServerSelectionTimeoutError
from VK_UserRelation import *
from DashGraphs import *


def index(request):
    return render(request, 'main/index.html')


def change_settings(request):
    info = json.load(open('config/config.json', 'r'))
    return render(request, 'main/changeSettings.html', info)


def change_settings_result(request):
    default = request.POST.get('default', '')

    if default:
        new_config = json.load(open('config/default_config.json', 'r'))
        json.dump(new_config, open('config/config.json', 'w'))
    else:
        # {% костыль %}
        json.dump(request.POST, open('config/config.json', 'w'))
        new_config = json.load(open('config/config.json', 'r'))
        try:
            new_config.pop('csrfmiddlewaretoken')
        except:
            pass
        json.dump(new_config, open('config/config.json', 'w'))
        # {% endкостыль %}

    return render(request, 'main/changeSettingsResult.html')


def get_domain_add(request):
    return render(request, 'main/add_user/getDomain.html')


def add_result(request):
    config = json.load(open('config/config.json', 'r'))
    info = {}

    try:
        vk_user = VK_UserInfo(token=config['vk_token'], domain=request.POST['domain'])
        config.pop('vk_token')
        user = vk_user.add_user_to_DBs(**config)

        info['info'] = {
            'first_name': user['main_info']['first_name'],
            'last_name':  user['main_info']['last_name'],
            'domain':     user['main_info']['domain'],
            'id':         user['main_info']['id']
        }
    except ConnectionError:
        info['error'] = 'no connection to the internet'
    except vk.exceptions.VkAPIError:
        info['error'] = 'user with input domain not found'
    except ServerSelectionTimeoutError:
        info['error'] = 'MongoDB is not connected'
    except ServiceUnavailable:
        info['error'] = 'Neo4j is not connected'
    except Exception:
        info['error'] = traceback.format_exc()

    return render(request, 'main/add_user/addResult.html', info)


def get_domain_info(request):
    return render(request, 'main/user_info/getDomain.html')


def get_info(request):
    config = json.load(open('config/config.json', 'r'))

    domain = request.POST['domain']
    info = {}

    try:
        mdb = MongoDB(host=config['MDB_HOST'], port=config['MDB_PORT'])

        info['info'] = mdb.load_user_info(domain=domain)
        info['fullname'] = mdb.get_fullname(domain=domain)
        info['id'] = info['info']['main_info']['id']
        info['domain'] = domain
        info['PHOTOS_GRAPH_PORT'] = PhotoLikesGraph(photos_list=info['info']['photos']['items']).run()
        info['POSTS_GRAPH_PORT'] = PostsLikesGraph(posts_list=info['info']['wall']['items']).run()
        info['GENDER_GRAPH_PORT'] = GenderGraph(friends_list=info['info']['friends']['items']).run()

    except ServerSelectionTimeoutError:
        info['error'] = 'MongoDB is not connected'
    except Exception:
        info['error'] = traceback.format_exc()

    return render(request, 'main/user_info/userInfo.html', info)


def get_domain_changes(request):
    return render(request, 'main/user_changes/getDomain.html')


def get_dates(request):
    config = json.load(open('config/config.json', 'r'))
    domain = request.POST['domain']
    info = {}

    try:
        mdb = MongoDB(host=config['MDB_HOST'], port=config['MDB_PORT'])

        if not mdb.check_domain(domain):
            raise ValueError('user with input domain not found in database')
        info['info'] = {
            'dates': mdb.get_user_info_dates(domain=domain),
            'domain': domain
        }
    except ServerSelectionTimeoutError:
        info['error'] = 'MongoDB is not connected'
    except ValueError as e:
        info['error'] = e
    except Exception:
        info['error'] = traceback.format_exc()

    return render(request, 'main/user_changes/getDates.html', info)


def get_changes(request):
    config = json.load(open('config/config.json', 'r'))
    args = {
        'date1':      request.POST['date1'],
        'date2':      request.POST['date2'],
        'domain':     request.POST['domain'],
        'mongo_host': config['MDB_HOST'],
        'mongo_port': config['MDB_PORT']
    }

    cmp_info = VK_UserAnalizer(**args).get_changes()
    info = {
        'info':   cmp_info,
        'domain': args['domain'],
        'id':     cmp_info['id']
    }

    return render(request, 'main/user_changes/getChanges.html', info)


def get_domains(request):
    return render(request, 'main/users_relations/getDomains.html')


def get_users_dates(request):
    config = json.load(open('config/config.json', 'r'))
    first_domain = request.POST['first_domain']
    second_domain = request.POST['second_domain']
    info = {}

    try:
        mdb = MongoDB(host=config['MDB_HOST'], port=config['MDB_PORT'])

        if not mdb.check_domain(first_domain):
            raise ValueError('user with first domain not found in database')
        if not mdb.check_domain(second_domain):
            raise ValueError('user with second domain not found in database')

        info = {
            'first_domain':  first_domain,
            'second_domain': second_domain,
            'first_user':    mdb.get_fullname(domain=first_domain),
            'second_user':   mdb.get_fullname(domain=second_domain),
            'first_dates':   mdb.get_user_info_dates(domain=first_domain),
            'second_dates':  mdb.get_user_info_dates(domain=second_domain)
        }
    except ServerSelectionTimeoutError:
        info['error'] = 'MongoDB is not connected'
    except ValueError as e:
        info['error'] = e
    except Exception:
        info['error'] = traceback.format_exc()

    return render(request, 'main/users_relations/getUsersDates.html', info)


def get_relations(request):
    config = json.load(open('config/config.json', 'r'))
    args = {
        'first_domain':  request.POST['first_domain'],
        'second_domain': request.POST['second_domain'],
        'date1':         request.POST['date1'],
        'date2':         request.POST['date2'],
        'mongo_host':    config['MDB_HOST'],
        'mongo_port':    config['MDB_PORT']
    }

    try:
        info = VK_UserRelation(**args).get_mutual_activity()
    except Exception:
        info = {'error': traceback.format_exc()}

    return render(request, 'main/users_relations/getRelations.html', info)