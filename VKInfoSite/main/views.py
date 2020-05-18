import json
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.conf import settings
from requests.exceptions import ConnectionError
from neobolt.exceptions import ServiceUnavailable
from . import mongo
from .neo4j import Neo4jStorage
from .vk_models import VKInfo
from .vk_analitics import VKAnalizer, VKRelation
from .decorators import unauthenticated_user, post_method, check_token


def login_page(request):
    logout(request)
    if 'username' not in request.POST or 'password' not in request.POST:
        return render(request, 'login.html')
    user = authenticate(
        username=request.POST['username'],
        password=request.POST['password']
    )
    if user is not None:
        if user.is_active:
            login(request, user)
            mongo.set_conn(
                host=settings.DATABASES['default']['HOST'],
                port=settings.DATABASES['default']['PORT'],
                db_name=settings.DATABASES['default']['NAME'])
            return redirect('/add_user/')
        else:
            return render(request, 'login.html', {'error': 'Error: user account is disabled!'})
    return render(request, 'login.html', {'error': 'Error: username and password are incorrect!'})


@unauthenticated_user
def change_settings(request):
    if not request.user.is_superuser:
        return redirect('/add_user/')
    info = {
        'title': 'Settings | VK Tracker',
        **json.load(open(settings.CONFIG, 'r'))
    }
    return render(request, 'main/settings/changeSettings.html', info)


@post_method
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
        'title': 'Settings | VK Tracker',
        'message_title': 'Change result',
        'message': 'Settings have been successfully changed.'
    }
    return render(request, 'info.html', info)


@unauthenticated_user
def add_user(request):
    info = {
        'title': 'Add user | VK Tracker',
    }
    return render(request, 'main/add_user/getDomain.html', info)


@check_token
@post_method
@unauthenticated_user
def add_user_result(request):
    config = json.load(open(settings.CONFIG, 'r'))
    error = ''

    try:
        vk_user = VKInfo.get_user(token=config['vk_token'], domain=request.POST['domain'])
        config.pop('vk_token')
        user_info = vk_user.get_all_info()

        storage = Neo4jStorage.connect(
            url=config['neo_url'],
            user=config['neo_user'],
            password=config['neo_pass']
        )
        storage.add_user(user_info)

        storage = mongo.VKInfoStorage.connect(db=mongo.get_conn())
        storage.add_user(user_info)

        info = {
            'title': 'User was added | VK Tracker',
            'first_name': user_info['main_info']['first_name'],
            'last_name': user_info['main_info']['last_name'],
            'domain': user_info['main_info']['domain']
        }
    except ConnectionError:
        error = 'No connection to the internet.'
    except ServiceUnavailable:
        error = 'Neo4j is not connected.'

    if error:
        info = {
            'title': 'Error | VK Tracker',
            'message_title': 'Error',
            'message': error
        }
        return render(request, 'info.html', info)

    return render(request, 'main/add_user/addResult.html', info)


@unauthenticated_user
def user_info(request):
    info = {
        'title': 'User information | VK Tracker',
    }
    return render(request, 'main/user_info/getDomain.html', info)


@post_method
@unauthenticated_user
def get_user_info(request):
    domain = request.POST['domain']
    storage = mongo.VKInfoStorage.connect(db=mongo.get_conn())

    info = {
        'title': 'User information | VK Tracker',
        'info': storage.get_user(domain=domain),
        'fullname': storage.get_fullname(domain=domain),
        'domain': domain
    }
    info['id'] = info['info']['main_info']['id']

    return render(request, 'main/user_info/userInfo.html', info)


@unauthenticated_user
def get_changes(request):
    info = {
        'title': 'Account changes | VK Tracker',
    }
    return render(request, 'main/user_changes/getDomain.html', info)


@post_method
@unauthenticated_user
def get_dates(request):
    domain = request.POST['domain']
    storage = mongo.VKInfoStorage.connect(db=mongo.get_conn())

    if not storage.check_domain(domain):
        info = {
            'title': 'Error | VK Tracker',
            'message_title': 'Error',
            'message': 'user with input domain not found in database'
        }
        return render(request, 'info.html', info)

    info = {
        'title': 'Account changes | VK Tracker',
        'dates': storage.get_user_info_dates(domain=domain),
        'domain': domain
    }
    return render(request, 'main/user_changes/getDates.html', info)


@post_method
@unauthenticated_user
def get_user_changes(request):
    domain = request.POST['domain']
    storage = mongo.VKInfoStorage.connect(db=mongo.get_conn())
    new_info = storage.get_user(
        domain=domain,
        date=request.POST['date1'])
    old_info = storage.get_user(
        domain=domain,
        date=request.POST['date2'])
    cmp_info = VKAnalizer(new_info=new_info, old_info=old_info).get_changes()
    info = {
        'title': 'Account changes | VK Tracker',
        'domain': domain,
        'id':     cmp_info['id'],
        **cmp_info
    }
    return render(request, 'main/user_changes/getChanges.html', info)


@unauthenticated_user
def get_mutual_activity(request):
    info = {
        'title': 'Mutual activity | VK Tracker'
    }
    return render(request, 'main/users_relations/getDomains.html', info)


@post_method
@unauthenticated_user
def get_users_dates(request):
    first_domain = request.POST['first_domain']
    second_domain = request.POST['second_domain']
    error = ''

    storage = mongo.VKInfoStorage.connect(db=mongo.get_conn())
    if not storage.check_domain(first_domain):
        error = 'user with first domain not found in database'
    if not storage.check_domain(second_domain):
        error = 'user with second domain not found in database'
    info = {
        'title': 'Mutual activity | VK Tracker',
        'first_domain':  first_domain,
        'second_domain': second_domain,
        'first_user':    storage.get_fullname(domain=first_domain),
        'second_user':   storage.get_fullname(domain=second_domain),
        'first_dates':   storage.get_user_info_dates(domain=first_domain),
        'second_dates':  storage.get_user_info_dates(domain=second_domain)
    }

    if error:
        info = {
            'title': 'Error | VK Tracker',
            'message_title': 'Error',
            'message': error
        }
        return render(request, 'info.html', info)

    return render(request, 'main/users_relations/getUsersDates.html', info)


@post_method
@unauthenticated_user
def get_relations(request):
    storage = mongo.VKInfoStorage.connect(db=mongo.get_conn())
    user1_info = storage.get_user(
        domain=request.POST['first_domain'],
        date=request.POST['date1'])
    user2_info = storage.get_user(
        domain=request.POST['second_domain'],
        date=request.POST['date2'])
    info = {
        'title': 'Mutual activity | VK Tracker',
        **VKRelation(user1_info=user1_info, user2_info=user2_info).get_mutual_activity()
    }
    return render(request, 'main/users_relations/getRelations.html', info)
