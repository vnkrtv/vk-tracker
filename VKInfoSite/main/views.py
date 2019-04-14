import os
import traceback

from django.shortcuts import render
from MongoDB import MongoDB
from VK_UserInfo import VK_UserInfo

# Create your views here.



def index(request):
    return render(request, 'main/index.html')



def getDomainAdd(request):
    return render(request, 'main/add_user/getDomain.html')

def addResult(request):
    token = open('token/token.txt', 'r').read()

    try:
        vk_user = VK_UserInfo(token=token, domain=request.POST['domain'])
        user = vk_user.addUserToDB()

        info = {'value': [
            {'Имя': user['main_info']['first_name']},
            {'Фамилия': user['main_info']['last_name']},
            {'domain': user['main_info']['domain']},
            {'id': user['main_info']['id']}]
        }
    except Exception as e:
        info = {'error': traceback.format_exc()}

    return render(request, 'main/add_user/addResult.html', info)



def getDomainChanges(request):
    return render(request, 'main/user_changes/getDomain.html')

def getOldInfo(request):
    token = open('token/token.txt', 'r').read()

    domain = request.POST['domain']

    try:
        user = VK_UserInfo(token=token, domain=domain)
        info = {}

        if os.path.exists('userdata/' + user.userFolder()):
            info['files'] = [file[0:-5] for file in os.listdir('userdata/' + user.userFolder())]
        else:
            info['files'] = 'user not found'
    except Exception as e:
        info = {'error': traceback.format_exc()}

    return render(request, 'main/user_changes/getOldInfo.html', info)

def getChanges(request):
    file = request.POST['file']
    return render(request, 'main/user_changes/getChanges.html')



def getDomainInfo(request):
    return render(request, 'main/user_info/getDomain.html')

def getInfo(request):
    try:
        vk_user = MongoDB().loadUserInfo(domain=request.POST['domain'])
        user = list(vk_user.values())[0]
        info = {'value': [
            {'Имя': user['main_info']['first_name']},
            {'Фамилия': user['main_info']['last_name']},
            {'domain': user['main_info']['domain']},
            {'id': user['main_info']['id']}]
        }
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

    return render(request, 'main/users_relations/getRelations.html')
