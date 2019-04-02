from django.shortcuts import render
from VK_UserInfo import VK_UserInfo

# Create your views here.

from VK_UserInfo import VK_UserInfo

def index(request):
    return render(request, 'main/homePage.html')

def getUserInfo(request):
    vk_user = VK_UserInfo('b224a255a3de4e95ece62460ff0e8bfa11e67e965daa7eec3b4394c0726540412befb451396083a646007', 'id96354931')
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
    return render(request, 'main/basic.html', info)