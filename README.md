# vk-tracker  

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
- ```git clone https://github.com/LeadNess/vk-tracker.git```
- ```cd vk-tracker```
- ```./build_for_linux``` - build application on host system
- ```./deploy_containers``` - configure settings for vk-tracker container and docker-compose, if allowed will be added as a service in systemd as vk-tracker.service. 

### Usage

You can run application using docker-compose:  
- ```git clone https://github.com/LeadNess/vk-tracker.git```
- ```cd vk-tracker```
- ```./deploy_containers```
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
VKInfoSite/dashboard/graphs.py                  215    173    20%
VKInfoSite/dashboard/views.py                    28     17    39%
VKInfoSite/main/decorators.py                    29      9    69%
VKInfoSite/main/models.py                        10      1    90%
VKInfoSite/main/mongo.py                         57      8    86%
VKInfoSite/main/neo4j.py                        104     33    68%
VKInfoSite/main/templatetags/main_extras.py      29      9    69%
VKInfoSite/main/views.py                        114     20    82%
VKInfoSite/main/vk_analytics.py                 362     96    73%
VKInfoSite/main/vk_models.py                    104     70    33%
VKInfoSite/vksearch/mongo.py                     18      9    50%
VKInfoSite/vksearch/views.py                    195    159    18%
VKInfoSite/vksearch/vkscripts.py                 16      4    75%
-----------------------------------------------------------------
TOTAL                                          1281    608    53%
```
For detailed report run:
- ```coverage report```  
- ```coverage html```  
- ```x-www-browser ./htmlcov/index.html``` for Linux or ```Invoke-Expression .\htmlcov\index.html``` for Windows

### Code inspection

For main app - ```pylint VKInfoSite/main/*.py```:  
- ```Your code has been rated at 10.00/10```