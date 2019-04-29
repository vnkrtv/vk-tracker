import traceback

from django.shortcuts import render
from requests.exceptions import ConnectionError
from neobolt.exceptions import ServiceUnavailable
from pymongo.errors import ServerSelectionTimeoutError
from VK_UserRelation import *

# Create your views here.


def index(request):
    return render(request, 'main/index.html')


def get_domain_add(request):
    return render(request, 'main/add_user/getDomain.html')


def add_result(request):
    info = {}

    try:
        vk_user = VK_UserInfo(token=open('token/token.txt', 'r').read(), domain=request.POST['domain'])
        user = vk_user.add_user_to_DBs()

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
    domain = request.POST['domain']
    info = {}

    try:
        info['info'] = MongoDB().load_user_info(domain=domain)
        info['fullname'] = MongoDB().get_fullname(domain=domain)
        info['id'] = info['info']['main_info']['id']
        info['domain'] = domain

    except ServerSelectionTimeoutError:
        info['error'] = 'MongoDB is not connected'
    except Exception:
        info['error'] = traceback.format_exc()

    return render(request, 'main/user_info/userInfo.html', info)


def get_domain_changes(request):
    return render(request, 'main/user_changes/getDomain.html')


def get_dates(request):
    domain = request.POST['domain']
    info = {}

    try:
        if not MongoDB().check_domain(domain):
            raise ValueError('user with input domain not found in database')
        info['info'] = {
            'dates': MongoDB().get_user_info_dates(domain=domain),
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
    date1 = request.POST['date1']
    date2 = request.POST['date2']
    domain = request.POST['domain']

    cmp_info = VK_UserAnalizer(domain=domain, date1=date1, date2=date2).get_changes()
    info = {
        'info':   cmp_info,
        'domain': domain,
        'id':     cmp_info['info']['id']
    }

    return render(request, 'main/user_changes/getChanges.html', info)


def get_domains(request):
    return render(request, 'main/users_relations/getDomains.html')


def get_users_dates(request):
    """

    :param request:
    :return:
    """
    first_domain = request.POST['first_domain']
    second_domain = request.POST['second_domain']
    info = {}

    try:
        if not MongoDB().check_domain(first_domain):
            raise ValueError('user with first domain not found in database')
        if not MongoDB().check_domain(second_domain):
            raise ValueError('user with second domain not found in database')

        info = {
            'first_domain':  first_domain,
            'second_domain': second_domain,
            'first_user':    MongoDB().get_fullname(domain=first_domain),
            'second_user':   MongoDB().get_fullname(domain=second_domain),
            'first_dates':   MongoDB().get_user_info_dates(domain=first_domain),
            'second_dates':  MongoDB().get_user_info_dates(domain=second_domain)
        }
    except ServerSelectionTimeoutError:
        info['error'] = 'MongoDB is not connected'
    except ValueError as e:
        info['error'] = e
    except Exception:
        info['error'] = traceback.format_exc()

    return render(request, 'main/users_relations/getUsersDates.html', info)


def get_relations(request):
    first_domain = request.POST['first_domain']
    second_domain = request.POST['second_domain']
    date1 = request.POST['date1']
    date2 = request.POST['date2']

    try:
        info = VK_UserRelation(first_domain, date1, second_domain, date2).get_mutual_activity()
    except Exception:
        info = {'error': traceback.format_exc()}

    return render(request, 'main/users_relations/getRelations.html', info)