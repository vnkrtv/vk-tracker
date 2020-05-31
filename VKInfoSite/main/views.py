# pylint: disable=no-member
"""Main app backend"""
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.conf import settings
from urllib3.exceptions import MaxRetryError
from . import mongo
from . import neo4j
from .vk_models import VKInfo
from .vk_analytics import VKAnalyzer, VKRelation
from .models import VKToken
from .decorators import unauthenticated_user, post_method, check_token


def login_page(request):
    """
    'login/' page view - redirect to 'add_user/' page
    in case of successful authorization
    """
    logout(request)
    if 'username' not in request.POST or 'password' not in request.POST:
        return render(request, 'login.html')
    user = authenticate(
        username=request.POST['username'],
        password=request.POST['password'])
    if user is not None:
        if user.is_active:
            neo4j.set_conn(
                url=settings.DATABASES['neo4j']['URL'],
                user=settings.DATABASES['neo4j']['USER'],
                password=settings.DATABASES['neo4j']['PASSWORD'])
            mongo.set_conn(
                host=settings.DATABASES['default']['HOST'],
                port=settings.DATABASES['default']['PORT'],
                db_name=settings.DATABASES['default']['NAME'])
            login(request, user)
            return redirect('/add_user/')
        return render(request, 'login.html', {'error': 'user account is disabled.'})
    return render(request, 'login.html', {'error': 'username and password are incorrect.'})


@unauthenticated_user
def change_settings(request):
    """
    'settings/' page view - displays page with user's VK token
    """
    query = VKToken.objects.filter(user__id=request.user.id)
    token = query[0].token if query else ''
    context = {
        'title': 'Settings | VK Tracker',
        'vk_token': token
    }
    return render(request, 'main/settings/changeSettings.html', context)


@post_method
@unauthenticated_user
def change_settings_result(request):
    """
    'change_settings_result/' page view - displays
    result of changing user's VK token
    """
    token = VKToken(
        user=request.user,
        token=request.POST['vk_token'])
    token.save()
    context = {
        'title': 'Settings | VK Tracker',
        'message_title': 'Change result',
        'message': 'Settings have been successfully changed.'
    }
    return render(request, 'info.html', context)


@unauthenticated_user
def add_user(request):
    """
    'add_user/' page view - displays page with domain input field
    """
    context = {
        'title': 'Add user | VK Tracker',
    }
    return render(request, 'main/add_user/getDomain.html', context)


@check_token
@post_method
@unauthenticated_user
def add_user_result(request):
    """
    'add_user/result/' page view - displays
    result of adding user to DBs
    """
    query = VKToken.objects.filter(user__id=request.user.id)
    token = query[0].token if query else ''

    try:
        vk_user = VKInfo.get_user(token=token, domain=request.POST['domain'])
        info = vk_user.get_all_info()

        neo4j_storage = neo4j.Neo4jStorage.connect(conn=neo4j.get_conn())
        neo4j_storage.add_user(info)

        mongo_storage = mongo.VKInfoStorage.connect(db=mongo.get_conn())
        mongo_storage.add_user(info)

        context = {
            'title': 'User was added | VK Tracker',
            'first_name': info['main_info']['first_name'],
            'last_name': info['main_info']['last_name'],
            'domain': info['main_info']['domain']
        }
    except MaxRetryError:
        context = {
            'title': 'Error | VK Tracker',
            'message_title': 'Error',
            'message': 'No connection to Neo4j. Is it running?'
        }
        return render(request, 'info.html', context)

    return render(request, 'main/add_user/addResult.html', context)


@unauthenticated_user
def user_info(request):
    """
    'user_info/' page view - displays page with domain input field
    """
    context = {
        'title': 'User information | VK Tracker',
    }
    return render(request, 'main/user_info/getDomain.html', context)


@post_method
@unauthenticated_user
def get_user_info(request):
    """
    'user_info/show_info/' page view - displays information
    about user and link to 'dashboard/${domain}' page
    """
    domain = request.POST['domain']
    storage = mongo.VKInfoStorage.connect(db=mongo.get_conn())
    info = storage.get_user(domain=domain)

    if not info:
        context = {
            'title': 'Error | VK Tracker',
            'message_title': 'Error',
            'message': "User's not found in base."
        }
        return render(request, 'info.html', context)

    context = {
        'title': 'User information | VK Tracker',
        'info': info,
        'fullname': storage.get_fullname(domain=domain),
        'domain': domain,
        'id': info['main_info']['id']
    }
    return render(request, 'main/user_info/userInfo.html', context)


@unauthenticated_user
def get_changes(request):
    """
    'user_changes/' page view - displays page with domain input field
    """
    context = {
        'title': 'Account changes | VK Tracker',
    }
    return render(request, 'main/user_changes/getDomain.html', context)


@post_method
@unauthenticated_user
def get_dates(request):
    """
    'user_changes/get_dates/' page view - displays page with
    2 date selectors for which user information was collected
    """
    domain = request.POST['domain']
    storage = mongo.VKInfoStorage.connect(db=mongo.get_conn())

    if not storage.check_domain(domain):
        context = {
            'title': 'Error | VK Tracker',
            'message_title': 'Error',
            'message': 'user with input domain not found in database'
        }
        return render(request, 'info.html', context)

    context = {
        'title': 'Account changes | VK Tracker',
        'dates': storage.get_user_info_dates(domain=domain),
        'domain': domain
    }
    return render(request, 'main/user_changes/getDates.html', context)


@post_method
@unauthenticated_user
def get_user_changes(request):
    """
    'user_changes/show/' page view - displays page with
    changes on the user’s page between two dates
    """
    domain = request.POST['domain']
    storage = mongo.VKInfoStorage.connect(db=mongo.get_conn())
    old_info = storage.get_user(
        domain=domain,
        date=request.POST['date2'])
    new_info = storage.get_user(
        domain=domain,
        date=request.POST['date1'])
    cmp_info = VKAnalyzer(old_info=old_info, new_info=new_info).get_changes()
    context = {
        'title': 'Account changes | VK Tracker',
        'domain': domain,
        'id':     cmp_info['id'],
        **cmp_info
    }
    return render(request, 'main/user_changes/getChanges.html', context)


@unauthenticated_user
def get_mutual_activity(request):
    """
    'users_relation/' page view - displays page with 2 domain input fields
    """
    context = {
        'title': 'Mutual activity | VK Tracker'
    }
    return render(request, 'main/users_relations/getDomains.html', context)


@post_method
@unauthenticated_user
def get_users_dates(request):
    """
    'users_relation/get_dates/' page view - displays page with 2 date
    selectors for 2 users which information about them was collected
    """
    first_domain = request.POST['first_domain']
    second_domain = request.POST['second_domain']
    error = ''

    storage = mongo.VKInfoStorage.connect(db=mongo.get_conn())
    if not storage.check_domain(first_domain):
        error = 'user with first domain not found in database'
    if not storage.check_domain(second_domain):
        error = 'user with second domain not found in database'
    context = {
        'title': 'Mutual activity | VK Tracker',
        'first_domain':  first_domain,
        'second_domain': second_domain,
        'first_user':    storage.get_fullname(domain=first_domain),
        'second_user':   storage.get_fullname(domain=second_domain),
        'first_dates':   storage.get_user_info_dates(domain=first_domain),
        'second_dates':  storage.get_user_info_dates(domain=second_domain)
    }

    if error:
        context = {
            'title': 'Error | VK Tracker',
            'message_title': 'Error',
            'message': error
        }
        return render(request, 'info.html', context)

    return render(request, 'main/users_relations/getUsersDates.html', context)


@post_method
@unauthenticated_user
def get_relations(request):
    """
    'users_relation/show/' page view - displays mutual activity of 2 users
    """
    storage = mongo.VKInfoStorage.connect(db=mongo.get_conn())
    user1_info = storage.get_user(
        domain=request.POST['first_domain'],
        date=request.POST['date1'])
    user2_info = storage.get_user(
        domain=request.POST['second_domain'],
        date=request.POST['date2'])
    context = {
        'title': 'Mutual activity | VK Tracker',
        **VKRelation(user1_info=user1_info, user2_info=user2_info).get_mutual_activity()
    }
    return render(request, 'main/users_relations/getRelations.html', context)
