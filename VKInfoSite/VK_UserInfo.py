from VK_User import *
from datetime import datetime as time
from time import clock, sleep
from GraphDB import GraphDB
from MongoDB import VKMongoDB


class VK_UserInfo(VK_User):
    _timeout = 0.35

    def __init__(self, token, domain):
        """

        :param token: vk token (must have all rights)
        :param domain: vk user domain
        """
        super(VK_UserInfo, self).__init__(token, domain)

    def get_main_info(self):
        """

        :return: dict of vk user main info
        """
        fields  = 'counters,photo_id,verified,sex,bdate,city,country,home_town,domain,contacts,site,education,universities,schools,'
        fields += 'status,followers_count,occupation,relatives,relation,personal,connections,activities,interests,about,career'

        try:
            main_info = self._user.users.get(user_ids=self._id,
                                             fields=fields,
                                             v='5.65')[0]
            main_info['counters'].pop('online_friends')
        except:
            main_info = None

        sleep(self._timeout)
        return main_info

    def get_friends(self):
        """

        :return: dict of vk user's friends
        {
            'count': quantity of user's friends,
            'items': {
                {
                    'first_name': ...,
                    'last_name': ...,
                    'bdate': ...,


                }
            ]
        }

        """
        try:
            friends = self._user.friends.get(user_id=self._id,
                                             fields='domain,sex,bdate,country,city,contacts,education',
                                             v='5.65')
            for friend in friends['items']:
                friend.pop('online')
        except:
            friends = None

        sleep(self._timeout)
        return friends

    def get_followers(self):
        """

        :return: dict of vk user's followers
        """
        try:
            followers = self._user.users.getFollowers(user_id=self._id,
                                                      fields='domain,sex,bdate,country,city,contacts,education',
                                                      v='5.65')
        except:
            followers = None

        sleep(self._timeout)
        return followers

    def get_photos(self):
        """

        :return: dict of
        """
        try:
            resp = self._user.photos.getAll(owner_id=self._id, count=200, photo_sizes=0, extended=0, v='5.65')
            sleep(self._timeout)

            photos = {
                'count': resp['count'],
                'items': []
            }

            code = """
                var photos = {photos};
                var res = [];
                var i = 0;
                while (i < photos.length) {{
                    var photo = {};
                    photo.photo_id = photos[i];
                    var likes = API.likes.getList({{
                                     "type": "photo",
                                     "owner_id": {user_id}},
                                     "item_id": photos[i],
                                     "filter": "likes",
                                     "extended": 1
                    }});
                    if (likes.f) {{
                        photo.likes = { "count": 0, "items": [] };
                    }} else {{
                        photo.likes = likes;
                    }}
                    
                    var comments = API.photos.getComments({{
                                     "owner_id": {user_id}},
                                     "photo_id": photos[i],
                                     "fields": "first_name,last_name",
                                     "extended": 1
                    }});
                    if (comments.f) {{
                        photo.comments = { "count": 0, "items": [] };
                    }} else {{
                        photo.comments = comments;
                    }}
                    
                    res.push(photo);
                    i = i + 1;
                }}
                return res;
            """

            photos_ids = [photo['id'] for photo in resp['items']]

            # 25 - max API requests per one execute method
            photos_groups = list(zip(*[iter(photos_ids)] * 12))
            remaining_photos_count = len(photos_ids) - 12 * len(photos_groups)
            photos_groups.append(photos_ids[len(photos_ids) - remaining_photos_count:])

            for photos_group in photos_groups:
                photos_list = list(photos_group)
                req_code = code.format(photos=photos_list, user_id=self._id).replace('\n', '').replace('  ', '')
                photos['items'] += self._user.execute(code=req_code, v='5.65')
                sleep(self._timeout)
        except:
            photos = {
                'count': 0,
                'items': []
            }
        return photos

    def get_wall(self):
        try:
            resp = self._user.wall.get(owner_id=self._id, count=100, photo_sizes=0, extended=0, v='5.65')
            sleep(self._timeout)

            wall = {
                'count': resp['count'],
                'items': []
            }

            code = """
                var posts = {posts};
                var res = [];
                var i = 0;
                while (i < posts.length) {{
                    var post = {};
                    post.post_id = posts[i].id;
                    post.text = posts[i].text
                    var likes = API.likes.getList({{
                                     "type": "post",
                                     "owner_id": {user_id}},
                                     "item_id": posts[i].id,
                                     "filter": "likes",
                                     "extended": 1
                    }});
                    if (likes.f) {{
                        post.likes = { "count": 0, "items": [] };
                    }} else {{
                        post.likes = likes;
                    }}
                    
                    if (posts[i].attachments) {{
                        post.attachments = posts[i].attachments;
                    }}            
        
                    var comments = API.wall.getComments({{
                                     "owner_id": {user_id}},
                                     "post_id": posts[i].id,
                                     "fields": "first_name,last_name",
                                     "extended": 1
                    }});
                    if (comments.f) {{
                        post.comments = { "count": 0, "items": [] };
                    }} else {{
                        post.comments = comments;
                    }}

                    res.push(post);
                    i = i + 1;
                }}
                return res;
            """
            posts = resp['items']

            # 25 - max API requests per one execute method
            posts_groups = list(zip(*[iter(posts)] * 12))
            remaining_posts_count = len(posts) - 12 * len(posts_groups)
            posts_groups.append(posts[len(posts) - remaining_posts_count:])

            for posts_group in posts_groups:
                posts_list = list(posts_group)
                req_code = code.format(posts=posts_list, user_id=self._id).replace('\n', '').replace('  ', '')
                wall['items'] += self._user.execute(code=req_code, v='5.65')
                sleep(self._timeout)
        except:
            wall = {
                'count': 0,
                'items': []
            }
        return wall

    def get_groups(self):
        try:
            groups = self._user.groups.get(user_id=self._id, count=200, extended=1,
                                                     fields='id,name,screen_name', v='5.65')
            for item in groups['items']:
                item.pop('is_advertiser')
                item.pop('is_member')
                item.pop('photo_200')
                item.pop('photo_100')
                item.pop('photo_50')
        except:
            groups = {
                'items': []
            }
        sleep(self._timeout)
        return groups

    def get_mutual_friends(self, id):
        try:
            friends = self._user.friends.getMutual(source_uid=self._id, target_uid=id, v='5.101')
        except:
            friends = None
        sleep(self._timeout)
        return friends

    def get_all_info(self):

        info = {}
        start = clock()

        print('Start loading information about %s\n' % (self._user_name + ' ' + self._user_surname))

        info['main_info'] = self.get_main_info()
        print('[%d s]Main information was loaded...\n' % (clock() - start))

        info['friends'] = self.get_friends()
        print('[%d s]Friends were loaded...\n' % (clock() - start))

        info['followers'] = self.get_followers()
        print('[%d s]Followers were loaded...\n' % (clock() - start))

        info['groups'] = self.get_groups()
        print('[%d s]Groups were loaded...\n' % (clock() - start))

        info['wall'] = self.get_wall()
        print('[%d s]Wallposts were loaded...\n' % (clock() - start))

        info['photos'] = self.get_photos()
        print('[%d s]Photos were loaded...\n' % (clock() - start))

        print('Information about %s was successfully loaded\n' % (self._user_name + ' ' + self._user_surname))

        date = time.now().timetuple()
        info['date'] = {
            'year': date[0],
            'month': date[1],
            'day': date[2],
            'hour': date[3],
            'minutes': date[4]
        }

        return info

    def add_user_to_DBs(self, mdb_host, mdb_port, neo_url, neo_user, neo_pass):
        """
        Add user to Mongo db and Neo5j db
        :param mongo_host:
        :param mongo_port:
        :param url:
        :param user:
        :param password:
        :return: json with vk user info
        """
        info = self.get_all_info()

        VKMongoDB(host=mdb_host, port=mdb_port).add_user(info)
        GraphDB(url=neo_url, user=neo_user, password=neo_pass).add_user(info)

        return info
