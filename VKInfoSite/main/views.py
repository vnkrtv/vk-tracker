import os

from django.shortcuts import render
from VK_UserInfo import VK_UserInfo

# Create your views here.

from VK_UserInfo import VK_UserInfo

def index(request):
    return render(request, 'main/homePage.html')

def getUserDomainShowData(request):
    return render(request, 'main/getUserDomainDataPage.html')

def getUserDomainChanges(request):
    return render(request, 'main/getUserDomainChangesPage.html')

def getUserDomains(request):
    return render(request, 'main/getUsersDomainsPage.html')

def getUserInfo(request):
    token = open('token/token.txt', 'r').read()
    vk_user = VK_UserInfo(token=token, domain=request.POST['domain'])
    user = vk_user.addUserToDatabase()

    info = {'value': [
        {'Имя': user['first_name']},
        {'Фамилия': user['last_name']},
        {'domain': user['domain']},
        {'id': user['id']},
        {'Инстаграмм': user['instagram']},
        {'Статус': user['status']},
        {'День рождения': user['bday']},
        {'Страна': user['country']},
        {'Город': user['city']}]
    }
    return render(request, 'main/userInfo.html', info)

def getUserOldInfo(request):
    token = open('token/token.txt', 'r').read()

    domain = request.POST['domain']
    user = VK_UserInfo(token=token, domain=domain)
    info = {}

    if os.path.exists('userdata/' + user.userFolder()):
        info['files'] = [file[0:-5] for file in os.listdir('userdata/' + user.userFolder())]
    else:
        info['files'] = 'user not found'

    return render(request, 'main/getUserOldInfo.html', info)

def getUserChanges(request):
    file = request.POST['file']

    return render(request, 'main/getUserChanges.html')

def getUsersRelations(request):
    first_domain  = request.POST['first_domain']
    second_domain = request.POST['second_domain']

    return render(request, 'main/getUsersRelations.html')
