"""Classes for loading VK user's info using VK API"""
import time
from datetime import datetime
import vk


class VKUser:
    """Base class for working with VK API"""

    _token: str
    _session: vk.API
    _domain: str
    _id: str
    _first_name: str
    _last_name: str
    _timeout: float = 0.35
    _api_version: str = '5.103'

    def open_session(self, token: str, domain: str) -> None:
        """
        Create VK API session using passed token, checks if passed domain is correct

        :param token: VK token with all rights
        :param domain: VK user domain
        """
        self._token = token
        self._session = vk.API(vk.Session(access_token=token))
        request = self._session.users.get(
            user_ids=domain,
            fields='domain',
            v=self._api_version
        )
        time.sleep(self._timeout)

        if not request or request[0]['domain'] != domain:
            raise vk.exceptions.VkException('Incorrect domain.')

        self._id = request[0]['id']
        self._first_name = request[0]['first_name']
        self._last_name = request[0]['last_name']

    def get_first_name(self) -> str:
        """
        Returns first name of user with passed domain

        :return: VK user first name
        """
        return self._first_name

    def get_last_name(self) -> str:
        """
        Returns last name of user with passed domain

        :return: VK user last name
        """
        return self._last_name

    def get_id(self) -> str:
        """
        Returns id of user with passed domain

        :return: VK user id
        """
        return self._id

    def get_domain(self) -> str:
        """
        Returns domain of user with passed domain

        :return: VK user domain
        """
        return self._domain


class VKInfo(VKUser):
    """Loading user's account info using VK API"""

    @staticmethod
    def get_user(token: str, domain: str):
        """
        Opens session with passed token for loading
        information about user with passed domain

        :param token: VK token with all rights
        :param domain: VK user domain
        :return: VKInfo object
        """
        obj = VKInfo()
        obj.open_session(token, domain)
        return obj

    def get_main_info(self) -> dict:
        """
        Loads user's page main info

        :return: dict with user's main info
        """
        fields = 'counters,photo_id,verified,sex,bdate,city,country,home_town,' \
                 'domain,contacts,site,education,universities,schools,status,' \
                 'followers_count,occupation,relatives,relation,personal,' \
                 'connections,activities,interests,about,career'

        main_info = self._session.users.get(user_ids=self._id,
                                            fields=fields,
                                            v=self._api_version)[0]
        main_info['counters'].pop('online_friends')
        time.sleep(self._timeout)
        return main_info

    def get_friends(self) -> dict:
        """
        Loads user's friends

        :return: dict
        {
            'count': quantity of user's friends,
            'items': [
                {
                    'id': ...,
                    'first_name': ...,
                    'last_name': ...,
                    'bdate': ...,
                    ...
                },
                ...
            ]
        }

        """
        fields = 'domain,sex,bdate,country,city,contacts,education'
        friends = self._session.friends.get(user_id=self._id,
                                            fields=fields,
                                            v=self._api_version)
        for friend in friends['items']:
            friend.pop('online')

        time.sleep(self._timeout)
        return friends

    def get_followers(self) -> dict:
        """
        Loads user's followers

        :return: dict
        {
            'count': quantity of user's followers,
            'items': [
                {
                    'id': ...,
                    'first_name': ...,
                    'last_name': ...,
                    'bdate': ...,
                    ...
                },
                ...
            ]
        }
        """
        fields = 'domain,sex,bdate,country,city,contacts,education'
        followers = self._session.users.getFollowers(user_id=self._id,
                                                     fields=fields,
                                                     v=self._api_version)
        time.sleep(self._timeout)
        return followers

    def get_photos(self) -> dict:
        """
        Loads user's photos

        :return: dict
        {
            'count': quantity of user's photos,
            'items': [
                {
                    'photo_id': ...,
                    'likes': {
                        'count': ...,
                        'items': [
                            {
                                'id': ...,
                                'first_name': ...,
                                'last_name': ...,

                            },
                            ...
                        ]
                    }
                    'comments': {
                        'count': ...,
                        'items': [ ... ]
                    }
                },
                ...
            ]
        }
        """
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
            req_code = code.format(
                photos=photos_list,
                user_id=self._id
            ).replace('True', 'true').replace('False', 'false')
            photos['items'] += self._session.execute(code=req_code, v=self._api_version)
            time.sleep(self._timeout)

        return photos

    def get_wall(self) -> dict:
        """
        Loads user's posts from wall

        :return: dict
        {
            'count': quantity of user's posts,
            'items': [
                {
                    'post_id': ...,
                    'test': ...,
                    'likes': {
                        'count': ...,
                        'items': [
                            {
                                'id': ...,
                                'first_name': ...,
                                'last_name': ...,

                            },
                            ...
                        ]
                    }
                    'comments': {
                        'count': ...,
                        'items': [ ... ]
                    }
                },
                ...
            ]
        }
        """
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
            req_code = code.format(
                posts=posts_list,
                user_id=self._id
            ).replace('True', 'true').replace('False', 'false')
            wall['items'] += self._session.execute(code=req_code, v=self._api_version)
            time.sleep(self._timeout)

        return wall

    def get_groups(self) -> dict:
        """
        Loads user's groups

        :return: dict
        {
            'count': quantity of user's groups,
            'items': {
                {
                    'id': ...,
                    'screen_name': ...,
                    'type': ...,
                    ...
                },
                ...
            ]
        }
        """
        groups = self._session.groups.get(user_id=self._id, count=200, extended=1,
                                          fields='id,name,screen_name', v=self._api_version)
        for item in groups['items']:
            item.pop('photo_200')
            item.pop('photo_100')
            item.pop('photo_50')

        time.sleep(self._timeout)
        return groups

    def get_mutual_friends(self, _id: str) -> dict:
        """
        Loads mutual friends for user with passed domain and input _id

        :param _id: VK user id
        :return: dict with mutual friends
        """
        friends = self._session.friends.getMutual(
            source_uid=self._id,
            target_uid=_id
            , v=self._api_version
        )
        time.sleep(self._timeout)
        return friends

    def get_all_info(self) -> dict:
        """
        Loads and returns all user's account info

        :return: dict with all info
        """
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
