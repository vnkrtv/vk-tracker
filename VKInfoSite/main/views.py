import traceback
import json
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.conf import settings
from requests.exceptions import ConnectionError
from neobolt.exceptions import ServiceUnavailable
from pymongo.errors import ServerSelectionTimeoutError
from vk.exceptions import VkAPIError
from .mongodb import VKInfoStorage
from .neo4j import Neo4jStorage
from .vk_models import VKInfo
from .vk_analitics import VKAnalizer, VKRelation


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


def login_page(request):
    logout(request)
    if 'username' not in request.POST or 'password' not in request.POST:
        return render(request, 'main/login.html')
    user = authenticate(
        username=request.POST['username'],
        password=request.POST['password']
    )
    if user is not None:
        if user.is_active:
            login(request, user)
            return redirect('/add_user/')
        else:
            return render(request, 'main/login.html', {'error': 'Error: user account is disabled!'})
    else:
        return render(request, 'main/login.html', {'error': 'Error: username and password are incorrect!'})


@unauthenticated_user
def change_settings(request):
    if not request.user.is_superuser:
        return redirect('/add_user/')
    info = json.load(open(settings.CONFIG, 'r'))
    return render(request, 'main/settings/changeSettings.html', info)


@unauthenticated_user
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

    info = {
        'title': 'Change result',
        'message': 'Settings have been successfully changed.'
    }
    return render(request, 'main/info.html', info)


@unauthenticated_user
def add_user(request):
    return render(request, 'main/add_user/getDomain.html')


@unauthenticated_user
def add_user_result(request):
    config = json.load(open(settings.CONFIG, 'r'))
    error = ''

    try:
        vk_user = VKInfo.get_user(token=config['vk_token'], domain=request.POST['domain'])
        config.pop('vk_token')
        user_info = vk_user.get_all_info()

        neodb = Neo4jStorage.connect(
            url=config['neo_url'],
            user=config['neo_user'],
            password=config['neo_pass']
        )
        neodb.add_user(user_info)

        mdb = VKInfoStorage.connect_to_mongodb(
            host=config['mdb_host'],
            port=config['mdb_port'],
            db_name=config['mdb_dbname']
        )
        mdb.add_user(user_info)

        info = {
            'first_name': user_info['main_info']['first_name'],
            'last_name': user_info['main_info']['last_name'],
            'domain': user_info['main_info']['domain']
        }
    except ConnectionError:
        error = 'No connection to the internet.'
    except VkAPIError:
        error = 'User with input domain not found.'
    except ServerSelectionTimeoutError:
        error = 'MongoDB is not connected.'
    except ServiceUnavailable:
        error = 'Neo4j is not connected.'
    except Exception:
        error = traceback.format_exc()
    if error:
        info = {
            'title': 'Error',
            'message': error
        }
        return render(request, 'main/info.html', info)
    return render(request, 'main/add_user/addResult.html', info)


@unauthenticated_user
def user_info(request):
    return render(request, 'main/user_info/getDomain.html')


@unauthenticated_user
def get_user_info(request):
    config = json.load(open(settings.CONFIG, 'r'))

    domain = request.POST['domain']
    info = {}

    try:
        mdb = VKInfoStorage.connect_to_mongodb(
            host=config['mdb_host'],
            port=config['mdb_port'],
            db_name=config['mdb_dbname']
        )

        info['info'] = mdb.get_user(domain=domain)
        info['fullname'] = mdb.get_fullname(domain=domain)
        info['id'] = info['info']['main_info']['id']
        info['domain'] = domain

    except ServerSelectionTimeoutError:
        info['error'] = 'MongoDB is not connected'
    except Exception:
        info['error'] = traceback.format_exc()

    return render(request, 'main/user_info/userInfo.html', info)


@unauthenticated_user
def get_changes(request):
    return render(request, 'main/user_changes/getDomain.html')


@unauthenticated_user
def get_dates(request):
    config = json.load(open(settings.CONFIG, 'r'))
    domain = request.POST['domain']
    error = ''

    try:
        mdb = VKInfoStorage.connect_to_mongodb(
            host=config['mdb_host'],
            port=config['mdb_port'],
            db_name=config['mdb_dbname']
        )

        if not mdb.check_domain(domain):
            error = 'user with input domain not found in database'
        info = {
            'dates': mdb.get_user_info_dates(domain=domain),
            'domain': domain
        }
        print(info)

    except ServerSelectionTimeoutError:
        error = 'MongoDB is not connected'
    except Exception:
        error = traceback.format_exc()

    if error:
        info = {
            'title': 'Error',
            'message': error
        }
        return render(request, 'main/info.html', info)

    return render(request, 'main/user_changes/getDates.html', info)


@unauthenticated_user
def get_user_changes(request):
    config = json.load(open(settings.CONFIG, 'r'))
    domain = request.POST['domain']
    mdb = VKInfoStorage.connect_to_mongodb(
        host=config['mdb_host'],
        port=config['mdb_port'],
        db_name=config['mdb_dbname']
    )
    new_info = mdb.get_user(
        domain=domain,
        date=request.POST['date1']
    )
    old_info = mdb.get_user(
        domain=domain,
        date=request.POST['date2']
    )
    cmp_info = VKAnalizer(new_info=new_info, old_info=old_info).get_changes()
    info = {
        'domain': domain,
        'id':     cmp_info['id'],
        **cmp_info
    }
    return render(request, 'main/user_changes/getChanges.html', info)


@unauthenticated_user
def get_mutual_activity(request):
    return render(request, 'main/users_relations/getDomains.html')


@unauthenticated_user
def get_users_dates(request):
    config = json.load(open(settings.CONFIG, 'r'))
    first_domain = request.POST['first_domain']
    second_domain = request.POST['second_domain']
    error = ''

    try:
        mdb = VKInfoStorage.connect_to_mongodb(
            host=config['mdb_host'],
            port=config['mdb_port'],
            db_name=config['mdb_dbname']
        )
        if not mdb.check_domain(first_domain):
            error = 'user with first domain not found in database'
        if not mdb.check_domain(second_domain):
            error = 'user with second domain not found in database'
        info = {
            'first_domain':  first_domain,
            'second_domain': second_domain,
            'first_user':    mdb.get_fullname(domain=first_domain),
            'second_user':   mdb.get_fullname(domain=second_domain),
            'first_dates':   mdb.get_user_info_dates(domain=first_domain),
            'second_dates':  mdb.get_user_info_dates(domain=second_domain)
        }
    except ServerSelectionTimeoutError:
        error = 'MongoDB is not connected'
    except Exception:
        error = traceback.format_exc()

    if error:
        info = {
            'title': 'Error',
            'message': error
        }
        return render(request, 'main/info.html', info)

    return render(request, 'main/users_relations/getUsersDates.html', info)


@unauthenticated_user
def get_relations(request):
    config = json.load(open(settings.CONFIG, 'r'))
    try:
        mdb = VKInfoStorage.connect_to_mongodb(
            host=config['mdb_host'],
            port=config['mdb_port'],
            db_name=config['mdb_dbname']
        )
        user1_info = mdb.get_user(
            domain=request.POST['first_domain'],
            date=request.POST['date1']
        )
        user2_info = mdb.get_user(
            domain=request.POST['second_domain'],
            date=request.POST['date2']
        )
        info = VKRelation(user1_info=user1_info, user2_info=user2_info).get_mutual_activity()
    except Exception:
        info = {'error': traceback.format_exc()}
    return render(request, 'main/users_relations/getRelations.html', info)
