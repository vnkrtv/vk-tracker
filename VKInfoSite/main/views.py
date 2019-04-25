import os
import traceback

from django.shortcuts import render
from VK_UserAnalizer import *

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

def getOldInfo(request):
    token = open('token/token.txt', 'r').read()
    domain = request.POST['domain']

    try:
        VK_UserInfo(token=token, domain=domain)
        info = {
            'info': {
                'dates':  MongoDB().getUserDates(domain=domain),
                'domain': domain
            }
        }

    except Exception as e:
        info = {'error': traceback.format_exc()}

    return render(request, 'main/user_changes/getOldInfo.html', info)

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

def getRelations(request):
    first_domain  = request.POST['first_domain']
    second_domain = request.POST['second_domain']

    try:

        info = {}

    except Exception as e:
        info = {'error': traceback.format_exc()}

    return render(request, 'main/users_relations/getRelations.html', info)
