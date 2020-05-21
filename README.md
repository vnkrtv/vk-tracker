# vk-tracker  

### Description
Web application for tracking VK users and searching users by specified filters.  
Implemented on django, data is stored in MongoDB and Neo4j.  
System features:
- loading and storing vk users information:
  - main information
  - groups
  - friends
  - followers
  - photos
  - posts
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
- ```git clone https://github.com/LeadNess/VKUserInfo.git```
- ```cd VKUserInfo```
- ```./build_for_linux``` - build application 
- ```./build_docker``` - create docker container

### Usage

You can run application using docker-compose:  
- ```git clone https://github.com/LeadNess/VKUserInfo.git```
- ```cd VKUserInfo```
- ```./build_docker```
- ```cd docker```
- ```docker-compose up```

These commands launch 3 related containers:

- vkuserinfo - with web application
- mongo - with MongoDB
- neo4j - with Neo4j

There two types of users in system:
- superusers
  - can change settings
  - can enter admin panel and add new users
- users

Both types of users can use all system features.

### Testing

Coming soon...
  
