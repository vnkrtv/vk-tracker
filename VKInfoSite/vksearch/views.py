import traceback
import json

from django.shortcuts import render
from requests.exceptions import ConnectionError
from .vk_search import *
from MongoDB import *
from SQLiteDB import *
from config import *

def get_search_params(request):
    return render(request, 'vksearch/search/searchPage.html')


def get_result(request):
    params = dict(request.POST)
    print(params)
    info = {}

    try:
        pass
    except Exception:
        info['error'] = traceback.format_exc()

    return render(request, 'vksearch/search/resultPage.html', info)


def get_new_philter_countries(request):
    db = SQLiteDB(db_file=DB_FILE)
    info = {
        'countries': [item for item in db.get_countries() if item[0] < 5]
    }
    return render(request, 'vksearch/add_philter/getCountry.html', info)


def get_new_philter_region(request):
    db = SQLiteDB(db_file=DB_FILE)
    country_id = request.POST['country'][0]
    regions = request.POST['regions'][0]
    info = {
        'regions': [item for item in db.get_regions(country_id=country_id) if regions in item[1]],
        'country_id': country_id
    }
    return render(request, 'vksearch/add_philter/getRegion.html', info)


def get_new_philter_cities(request):
    region_id = request.POST['region']
    country_id = request.POST['country_id']
    cities_num = int(request.POST['cities_num'])
    cities = request.POST['cities'][0]
    db = SQLiteDB(db_file=DB_FILE)
    info = {
        'cities': [item for item in db.get_cities(country_id=country_id, region_id=region_id) if cities in item[1]],
        'cities_num': list(range(cities_num)),
        'country_id': country_id,
        'region_id': region_id
    }
    return render(request, 'vksearch/add_philter/getCities.html', info)


def get_new_philter_universities(request):
    print(request.POST)
    country_id = request.POST['country_id']
    cities = []
    for key in request.POST:
        if 'city' in key:
            cities.append(int(request.POST[key]))
    if 'university_set' in request.POST:
        universities_num = int(request.POST['universities_num'])
    print(cities)
    db = SQLiteDB(db_file=DB_FILE)
    info = {
        'cities': [item for item in db.get_universities(country_id=country_id, city_id=city_id)],
        'universities_num': list(range(universities_num)),
        'country_id': country_id,
    }
    return render(request, 'vksearch/add_philter/getUniversities.html', info)


def get_new_philter_friends_and_groups(request):
    region_id = request.POST['region']
    country_id = request.POST['country_id']
    cities_num = int(request.POST['cities_num'])
    cities = request.POST['cities'][0]
    db = SQLiteDB(db_file=DB_FILE)
    info = {
        'cities': [item for item in db.get_cities(country_id=country_id, region_id=region_id) if cities in item[1]],
        'cities_num': list(range(cities_num)),
        'country_id': country_id,
        'region_id': region_id
    }
    return render(request, 'vksearch/add_philter/getGroupsAndFriends.html', info)


def add_new_philter(request):
    return render(request, 'vksearch/add_philter/addPhilter.html')


def get_new_philter(request):
    info = {
        'philter_name': request.POST['philter_name'][0]
    }
    return render(request, 'vksearch/add_philter/getNewPhilter.html', info)