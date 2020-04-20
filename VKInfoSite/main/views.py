import traceback
import json

from django.shortcuts import render
from requests.exceptions import ConnectionError
from neobolt.exceptions import ServiceUnavailable
from pymongo.errors import ServerSelectionTimeoutError
from VK_UserRelation import *
from django.conf import settings


def index(request):
    return render(request, 'main/index.html')


def change_settings(request):
    info = json.load(open(settings.CONFIG, 'r'))
    return render(request, 'main/changeSettings.html', info)


def change_settings_result(request):
    default = request.POST.get('default', '')

    if default:
        new_config = json.load(open(settings.CONFIG, 'r'))
        json.dump(new_config, open(settings.CONFIG, 'w'))
    else:
        # {% костыль %}
        json.dump(request.POST, open(settings.CONFIG, 'w'))
        new_config = json.load(open(settings.CONFIG, 'r'))
        try:
            new_config.pop('csrfmiddlewaretoken')
        except:
            pass
        new_config['mdb_port'] = int(new_config['mdb_port'])
        json.dump(new_config, open(settings.CONFIG, 'w'))
        # {% endкостыль %}

    return render(request, 'main/changeSettingsResult.html')


def add_user(request):
    return render(request, 'main/add_user/getDomain.html')


def add_result(request):
    config = json.load(open(settings.CONFIG, 'r'))
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
    except:
        info['error'] = traceback.format_exc()

    return render(request, 'main/add_user/addResult.html', info)


def user_info(request):
    return render(request, 'main/user_info/getDomain.html')


def get_info(request):
    config = json.load(open(settings.CONFIG, 'r'))

    domain = request.POST['domain']
    info = {}

    try:
        mdb = VKMongoDB(host=config['mdb_host'], port=config['mdb_port'])

        info['info'] = mdb.load_user_info(domain=domain)
        info['fullname'] = mdb.get_fullname(domain=domain)
        info['id'] = info['info']['main_info']['id']
        info['domain'] = domain

    except ServerSelectionTimeoutError:
        info['error'] = 'MongoDB is not connected'
    except Exception:
        info['error'] = traceback.format_exc()

    return render(request, 'main/user_info/userInfo.html', info)


def get_changes(request):
    return render(request, 'main/user_changes/getDomain.html')


def get_dates(request):
    config = json.load(open(settings.CONFIG, 'r'))
    domain = request.POST['domain']
    info = {}

    try:
        mdb = VKMongoDB(host=config['mdb_host'], port=config['mdb_port'])

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


def get_user_changes(request):
    config = json.load(open(settings.CONFIG, 'r'))
    args = {
        'date1':      request.POST['date1'],
        'date2':      request.POST['date2'],
        'domain':     request.POST['domain'],
        'mongo_host': config['mdb_host'],
        'mongo_port': config['mdb_port']
    }

    cmp_info = VK_UserAnalizer(**args).get_changes()
    info = {
        'info':   cmp_info,
        'domain': args['domain'],
        'id':     cmp_info['id']
    }

    return render(request, 'main/user_changes/getChanges.html', info)


def get_mutual_activity(request):
    return render(request, 'main/users_relations/getDomains.html')


def get_users_dates(request):
    config = json.load(open(settings.CONFIG, 'r'))
    first_domain = request.POST['first_domain']
    second_domain = request.POST['second_domain']
    info = {}

    try:
        mdb = VKMongoDB(host=config['mdb_host'], port=config['mdb_port'])

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
    config = json.load(open(settings.CONFIG, 'r'))
    args = {
        'first_domain':  request.POST['first_domain'],
        'second_domain': request.POST['second_domain'],
        'date1':         request.POST['date1'],
        'date2':         request.POST['date2'],
        'mongo_host':    config['mdb_host'],
        'mongo_port':    config['mdb_port']
    }

    try:
        info = VK_UserRelation(**args).get_mutual_activity()
    except Exception:
        info = {'error': traceback.format_exc()}

    return render(request, 'main/users_relations/getRelations.html', info)


