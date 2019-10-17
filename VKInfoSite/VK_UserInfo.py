import vk

from datetime import datetime as time
from time import clock, sleep
from GraphDB import GraphDB
from MongoDB import VKMongoDB


class VK_UserInfo:
    _timeout = 0.35

    def __init__(self, token, domain):
        """

        :param token: vk token (must have all rights)
        :param domain: vk user domain
        """

        self._token = token
        self._user = vk.API(vk.Session(access_token=token))

        self._id = self._user.users.get(user_ids=domain, v='5.65')[0]['id']
        self._user_name = self._user.users.get(user_ids=domain, v='5.65')[0]['first_name']
        self._user_surname = self._user.users.get(user_ids=domain, v='5.65')[0]['last_name']

    def get_first_name(self):
        return self._user_name

    def get_last_name(self):
        return self._user_surname

    def get_id(self):
        return self._id

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
                'photos': {
                    'count': len(resp['items']),
                    'items': []
                     }
            }

            for item in resp['items']:

                photo = {
                    'photo_id': item['id']
                }

                try:
                    photo['likes'] = self._user.likes.getList(type='photo', owner_id=self._id, item_id=photo['photo_id'],
                                                              filter='likes', extended=1, v='5.65')
                except:
                    photo['likes'] = {
                        'count': 0,
                        'items': []
                    }

                sleep(self._timeout)

                try:
                    photo['comments'] = self._user.photos.getComments(owner_id=self._id, photo_id=photo['photo_id'], extended=1,
                                                                      fields='first_name,last_name', v='5.65')
                except:
                    photo['comments'] = {
                        'count': 0,
                        'items': []
                    }

                photos['photos']['items'].append(photo)
                sleep(self._timeout)
        except:
            photos = {
                'photos': {
                    'count': 0,
                    'items': []
                }
            }

        return photos['photos']

    def get_wall(self):
        try:
            resp = self._user.wall.get(owner_id=self._id, count=100, photo_sizes=0, extended=0, v='5.65')
            sleep(self._timeout)

            wall = {
                'wall': {
                    'count': len(resp['items']),
                    'items': []
                }
            }

            for item in resp['items']:

                post = {
                    'text':    item['text'],
                    'post_id': item['id']
                }

                try:
                    post['likes'] = self._user.likes.getList(type='post', owner_id=self._id, item_id=post['post_id'],
                                                             filter='likes', extended=1, v='5.65')
                except:
                    post['likes'] = {
                        'count': 0,
                        'items': []
                    }

                sleep(self._timeout)

                try:
                    post['attachments'] = item['attachments']
                except:
                    pass

                try:
                    post['comments'] = self._user.photos.getComments(owner_id=self._id, post_id=post['post_id'], extended=1,
                                                                     fields='first_name,last_name', v='5.65')
                except:
                    post['comments'] = {
                        'count': 0,
                        'items': []
                    }

                wall['wall']['items'].append(post)
                sleep(self._timeout)
        except:
            wall = {
                'wall': {
                    'count': 0,
                    'items': []
                }
            }

        return wall['wall']

    def get_groups(self):
        try:
            groups = {}
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
