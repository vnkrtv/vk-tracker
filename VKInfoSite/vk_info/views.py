from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.

from VK_UserInfo import VK_UserInfo

def index(request):
    responce = open('VK_Site/index.html').read()
    return HttpResponse(responce)