# vk-tracker  
[![Build Status](https://travis-ci.com/vnkrtv/vk-tracker.svg?branch=master)](https://travis-ci.com/vnkrtv/vk-tracker)
![Docker](https://github.com/vnkrtv/vk-tracker/workflows/Docker/badge.svg)
![Ubuntu](https://github.com/vnkrtv/vk-tracker/workflows/Ubuntu/badge.svg)

### Description
Web application for tracking VK users and searching users by specified filters.  
Implemented on django and dash, data is stored in MongoDB and Neo4j.  
System features:
- loading and storing vk users information:
  - main information
  - groups
  - friends
  - followers
  - photos
  - posts  
- visualization of user information using Dash:
  - age distribution of user friends as graph pie chart
  - cities distribution of user friends as graph pie chart
  - universities distribution of user friends as graph pie chart
  - countries distribution of user friends as graph pie chart
  - gender distribution of user friends as graph pie chart
  - user friends scatter plot with 3 axis - mutual friends, likes and comments on user's page 
- tracking changes on the user page - show all changes between page information collected in different time  
- shows 2 user relationship:
  - mutual friends  
  - mutual groups  
  - comments and likes on photos and posts of both users, if any
- adding specified search filters with the possibility of using them in various configurations. Filter fields:
  - cities - search among users from current cities
  - groups - search among groups followers
  - friends - search among users friends
  - universities - search among users from current universities

Requirements:
- vk token with all permissions

### Installation
- ```git clone https://github.com/vnkrtv/vk-tracker.git```
- ```cd vk-tracker```
- ```./deploy/build_for_linux``` - build application on host system
- ```./deploy/deploy_containers``` - configure settings for vk-tracker container and docker-compose, if allowed will be added as a service in systemd as vk-tracker.service. 

### Usage

You can run application using docker-compose:  
- ```git clone https://github.com/vnkrtv/vk-tracker.git```
- ```cd vk-tracker```
- ```./deploy/deploy_containers```
- ```docker-compose up```

These commands launch 3 related containers:

- vk-tracker - with web application
- mongo - with MongoDB
- neo4j - with Neo4j

There two types of users in system:
- superusers
  - can enter admin panel and add new users
- users

Both types of users can use all system features and have their own tokens.

### Testing

Run all tests with coverage by running (venv must be activated):   
- ```coverage run VKInfoSite/runtests.py```

```
Name                                          Stmts   Miss  Cover
-----------------------------------------------------------------
VKInfoSite/dashboard/graphs.py                  141     18    87%
VKInfoSite/dashboard/views.py                    33     12    64%
VKInfoSite/main/decorators.py                    29      9    69%
VKInfoSite/main/models.py                        10      1    90%
VKInfoSite/main/mongo.py                         57      8    86%
VKInfoSite/main/neo4j.py                        104     13    88%
VKInfoSite/main/templatetags/main_extras.py      30      9    70%
VKInfoSite/main/views.py                        118     13    89%
VKInfoSite/main/vk_analytics.py                 355     95    73%
VKInfoSite/main/vk_api.py                       104     70    33%
VKInfoSite/vksearch/mongo.py                     19      0   100%
VKInfoSite/vksearch/views.py                    196     37    81%
VKInfoSite/vksearch/vk_scripts.py                17      4    76%
-----------------------------------------------------------------
TOTAL                                          1213    289    76%
```
For detailed report run:
- ```coverage report```  
- ```coverage html```  
- ```x-www-browser ./htmlcov/index.html``` for Linux or ```Invoke-Expression .\htmlcov\index.html``` for Windows

### Code inspection

For main, vksearch, dashboard apps and tests - ```pylint --disable=duplicate-code VKInfoSite/{main/*.py,vksearch,dashboard,tests}```:  
- ```Your code has been rated at 10.00/10```
  
Duplicate code option disabled as pylint swears on vk script code.
