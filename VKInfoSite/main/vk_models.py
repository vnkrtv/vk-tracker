import vk
import time
from datetime import datetime


class VKUser:

    _token = ''
    _session = None
    _domain = ''
    _id = ''
    _first_name = ''
    _last_name = ''

    def open_session(self, token: str, domain: str):
        self._token = token
        self._session = vk.API(vk.Session(access_token=token))
        self._domain = self._session.users.get(user_ids=domain, fields='domain', v='5.65')[0]['domain']

        if self._domain != domain:
            raise Exception('wrong domain')

        self._id = self._session.users.get(user_ids=domain, v='5.65')[0]['id']
        self._first_name = self._session.users.get(user_ids=domain, v='5.65')[0]['first_name']
        self._last_name = self._session.users.get(user_ids=domain, v='5.65')[0]['last_name']

    def get_first_name(self):
        return self._first_name

    def get_last_name(self):
        return self._last_name

    def get_id(self):
        return self._id

    def get_domain(self):
        return self._domain


class VKInfo(VKUser):

    _timeout = 0.35
    _api_version = '5.103'

    @staticmethod
    def get_user(token: str, domain: str):
        obj = VKInfo()
        obj.open_session(token, domain)
        time.sleep(0.35)
        return obj

    def get_main_info(self) -> dict:
        """

        :return: dict of vk user main info
        """
        fields = 'counters,photo_id,verified,sex,bdate,city,country,home_town,domain,contacts,site,education,universities,schools,'
        fields += 'status,followers_count,occupation,relatives,relation,personal,connections,activities,interests,about,career'

        try:
            main_info = self._session.users.get(user_ids=self._id,
                                             fields=fields,
                                             v=self._api_version)[0]
            main_info['counters'].pop('online_friends')
        except:
            main_info = None

        time.sleep(self._timeout)
        return main_info

    def get_friends(self) -> dict:
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
            friends = self._session.friends.get(user_id=self._id,
                                                fields='domain,sex,bdate,country,city,contacts,education',
                                                v=self._api_version)
            for friend in friends['items']:
                friend.pop('online')
        except:
            friends = None

        time.sleep(self._timeout)
        return friends

    def get_followers(self) -> dict:
        """

        :return: dict of vk user's followers
        """
        try:
            followers = self._session.users.getFollowers(user_id=self._id,
                                                         fields='domain,sex,bdate,country,city,contacts,education',
                                                         v='5.65')
        except:
            followers = []

        time.sleep(self._timeout)
        return followers

    def get_photos(self) -> dict:
        """

        :return: dict of
        """
        try:
            resp = self._session.photos.getAll(
                owner_id=self._id,
                count=200,
                photo_sizes=0,
                extended=0,
                v=self._api_version
            )
            time.sleep(self._timeout)

            photos = {
                'count': resp['count'],
                'items': []
            }

            code = """
                var photos = {photos};
                var res = [];
                var i = 0;
                while (i < photos.length) {{
                    var photo = {{}};
                    photo.photo_id = photos[i];
                    var likes = API.likes.getList({{
                                     "type": "photo",
                                     "owner_id": {user_id},
                                     "item_id": photos[i],
                                     "filter": "likes",
                                     "extended": 1
                    }});
                    if (likes) {{
                        photo.likes = likes;
                    }} else {{
                        photo.likes = {{ "count": 0, "items": [] }};
                    }}

                    var comments = API.photos.getComments({{
                                     "owner_id": {user_id},
                                     "photo_id": photos[i],
                                     "fields": "first_name,last_name",
                                     "extended": 1
                    }});
                    if (comments) {{
                        photo.comments = comments;
                    }} else {{
                        photo.comments = {{ "count": 0, "items": [] }};
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
                photos['items'] += self._session.execute(code=req_code, v=self._api_version)
                time.sleep(self._timeout)
        except:
            photos = {
                'count': 0,
                'items': []
            }
        return photos

    def get_wall(self) -> dict:
        try:
            resp = self._session.wall.get(
                owner_id=self._id,
                count=100,
                photo_sizes=0,
                extended=0,
                v=self._api_version
            )
            time.sleep(self._timeout)

            wall = {
                'count': resp['count'],
                'items': []
            }

            code = """
                var posts = {posts};
                var res = [];
                var i = 0;
                while (i < posts.length) {{
                    var post = {{}};
                    post.post_id = posts[i].id;
                    post.text = posts[i].text;
                    var likes = API.likes.getList({{
                                     "type": "post",
                                     "owner_id": {user_id},
                                     "item_id": posts[i].id,
                                     "filter": "likes",
                                     "extended": 1
                    }});
                    if (likes) {{
                        post.likes = likes;
                    }} else {{
                        post.likes = {{ "count": 0, "items": [] }};
                    }}

                    if (posts[i].attachments) {{
                        post.attachments = posts[i].attachments;
                    }}            

                    var comments = API.wall.getComments({{
                                     "owner_id": {user_id},
                                     "post_id": posts[i].id,
                                     "fields": "first_name,last_name",
                                     "extended": 1
                    }});
                    if (comments) {{
                        post.comments = comments;
                    }} else {{
                        post.comments = {{ "count": 0, "items": [] }};
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
                posts_list = []
                for post in posts_group:
                    posts_list.append({
                        'id': post['id'],
                        'text': post['text']
                    })
                    if 'attachments' in post:
                        posts_list[-1]['attachments'] = post['attachments']
                req_code = code.format(posts=posts_list, user_id=self._id).replace('\n', '').replace('  ', '')
                wall['items'] += self._session.execute(code=req_code, v=self._api_version)
                time.sleep(self._timeout)
        except:
            wall = {
                'count': 0,
                'items': []
            }
        return wall

    def get_groups(self) -> dict:
        try:
            groups = self._session.groups.get(user_id=self._id, count=200, extended=1,
                                              fields='id,name,screen_name', v=self._api_version)
            for item in groups['items']:
                item.pop('photo_200')
                item.pop('photo_100')
                item.pop('photo_50')
        except:
            groups = {
                'items': []
            }
        time.sleep(self._timeout)
        return groups

    def get_mutual_friends(self, _id: str) -> dict:
        try:
            friends = self._session.friends.getMutual(source_uid=self._id, target_uid=_id, v=self._api_version)
        except:
            friends = []
        time.sleep(self._timeout)
        return friends

    def get_all_info(self) -> dict:
        date = datetime.now().timetuple()
        info = {
            'main_info': self.get_main_info(),
            'friends': self.get_friends(),
            'followers': self.get_followers(),
            'groups': self.get_groups(),
            'wall': self.get_wall(),
            'photos': self.get_photos(),
            'date': {
                'year': date[0],
                'month': date[1],
                'day': date[2],
                'hour': date[3],
                'minutes': date[4]
            }
        }
        return info


class VKUserActivity(VKUser):

    def check_user_activity(self):
        user = self._session.users.get(user_ids=self._domain, fields='last_seen,online', v='5.103')[0]

        is_online = user['online']
        last_seen_timestamp = user['last_seen']['time']
        last_seen_platform = user['last_seen']['platform'] - 1

        # self.load_activity(last_seen_timestamp, is_online, last_seen_platform)

    def get_activity(self):
        def parse_info(start_monitoring_timestamp, activity_list):
            # strtime = time.strftime('%Y-%m-%d %H:%M:%S')
            platform_dict = {
                1: 'm.vk.com',
                2: 'iPhone app',
                3: 'iPad app',
                4: 'Android app',
                5: 'Windows Phone app',
                6: 'Windows 8 app',
                7: 'web (vk.com)',
                8: 'VK Mobile'
            }

            activity = []
            for info in activity_list:
                delta = (info & 0b111111111111111111111111111)
                online = (info >> 31)
                platform = (info >> 28 & 0b111) + 1
                timestamp = start_monitoring_timestamp + delta
                last_seen_time = datetime.fromtimestamp(timestamp)
                """
                activity.append({
                    'online':   online,
                    'platform': platform_dict[platform],
                    'minute':   last_seen_time.minute,
                    'hour':     last_seen_time.hour,
                    'day':      last_seen_time.day,
                    'month':    last_seen_time.month,
                    'year':     last_seen_time.year
                })
                """
                activity.append({
                    'online':   online,
                    'platform': platform_dict[platform],
                    'time': last_seen_time.strftime('%Y-%m-%d %H:%M:%S')
                })
            return activity

        #with open(CONFIG_FILE, 'r') as file:
        #    config = json.load(file)
        #    mdb = VKActivityMongoDB(host=config['mdb_host'], port=config['mdb_port'])
        #    activity = parse_info(*mdb.get_activity(self._id))
        #return activity

