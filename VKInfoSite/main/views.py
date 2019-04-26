import os
import traceback

from django.shortcuts import render
from VK_UserRelation import *

# Create your views here.


def index(request):
    return render(request, 'main/index.html')



def getDomainAdd(request):
    return render(request, 'main/add_user/getDomain.html')

def addResult(request):
    token = open('token/token.txt', 'r').read()

    try:
        vk_user = VK_UserInfo(token=token, domain=request.POST['domain'])
        user    = vk_user.addUserToDB()

        value = {
            'info': {
                'first_name': user['main_info']['first_name'],
                'last_name':  user['main_info']['last_name'],
                'domain':     user['main_info']['domain'],
                'id':         user['main_info']['id']
            }
        }
    except Exception as e:
        value = {'error': traceback.format_exc()}

    return render(request, 'main/add_user/addResult.html', value)



def getDomainChanges(request):
    return render(request, 'main/user_changes/getDomain.html')

def getDates(request):
    domain = request.POST['domain']

    try:
        if not MongoDB().checkDomain(domain):
            raise Exception('user with input domain not found in database')
        info = {
            'info': {
                'dates':  MongoDB().getUserDates(domain=domain),
                'domain': domain
            }
        }

    except Exception as e:
        info = {'error': traceback.format_exc()}

    return render(request, 'main/user_changes/getDates.html', info)

def getChanges(request):
    date1  = request.POST['date1']
    date2  = request.POST['date2']
    domain = request.POST['domain']

    try:
        info = {
            'info': VK_UserAnalizer(domain=domain, date1=date1, date2=date2).getChanges()
        }
        info['domain'] = info['info']['domain']
        info['id']     = info['info']['id']
    except Exception as e:
        info = {'error': traceback.format_exc()}

    return render(request, 'main/user_changes/getChanges.html', info)



def getDomainInfo(request):
    return render(request, 'main/user_info/getDomain.html')

def getInfo(request):
    try:
        info = {
            'info': MongoDB().loadUserInfo(domain=request.POST['domain'])
        }
        info['domain']   = info['info']['main_info']['domain']
        info['id']       = info['info']['main_info']['id']
        info['fullname'] = info['info']['main_info']['first_name'] + ' ' + info['info']['main_info']['last_name']
    except Exception as e:
        info = {'error': traceback.format_exc()}

    return render(request, 'main/user_info/userInfo.html', info)



def getDomains(request):
    return render(request, 'main/users_relations/getDomains.html')

def getUsersDates(request):
    first_domain  = request.POST['first_domain']
    second_domain = request.POST['second_domain']

    try:
        if not MongoDB().checkDomain(first_domain):
            raise Exception('user with first domain not found in database')
        if not MongoDB().checkDomain(second_domain):
            raise Exception('user with second domain not found in database')

        info = {
            'first_domain': first_domain,
            'second_domain': second_domain,
            'first_user': MongoDB().getFullname(domain=first_domain),
            'second_user': MongoDB().getFullname(domain=second_domain),
            'first_dates': MongoDB().getUserDates(domain=first_domain),
            'second_dates': MongoDB().getUserDates(domain=second_domain)
        }

    except Exception as e:
        info = {'error': traceback.format_exc()}

    return render(request, 'main/users_relations/getUsersDates.html', info)


def getRelations(request):
    first_domain  = request.POST['first_domain']
    second_domain = request.POST['second_domain']
    date1 = request.POST['date1']
    date2 = request.POST['date2']

    try:
        info = VK_UserRelation(first_domain, date1, second_domain, date2).getActivity()
    except Exception as e:
        info = {'error': traceback.format_exc()}

    print(info)

    return render(request, 'main/users_relations/getRelations.html', info)
