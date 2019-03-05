import os
import shelve
import vk

from time import sleep, clock, ctime
from Database import GraphDatabase

token = 'b224a255a3de4e95ece62460ff0e8bfa11e67e965daa7eec3b4394c0726540412befb451396083a646007'
domain = 'durov'


class VK_UserInfo:
    _timeout = 0.35

    def __init__(self, token, domain):

        self._token = token
        self._user = vk.API(vk.Session(access_token=token))

        self._id = self._user.users.get(user_ids=domain, v='5.65')[0]['id']
        self._user_name = self._user.users.get(user_ids=domain, v='5.65')[0]['first_name']
        self._user_surname = self._user.users.get(user_ids=domain, v='5.65')[0]['last_name']


    def userMainInfo(self):
        fields  = 'counters,photo_id,verified,sex,bdate,city,country,home_town,domain,contacts,site,education,universities,schools,'
        fields += 'status,followers_count,occupation,relatives,relation,personal,connections,activities,interests,about,career'

        try:
            main_info = self._user.users.get(user_ids=self._id, fields=fields, v='5.65')[0]
            main_info['counters'].pop('online_friends')
        except:
            main_info = None

        sleep(self._timeout)
        return main_info

    def userFriends(self):
        try:
            friends = self._user.friends.get(user_id=self._id, fields='domain,sex,bdate,country', v='5.65')
            for friend in friends['items']:
                friend.pop('online')
        except:
            friends = None

        sleep(self._timeout)
        return friends

    def userFollowers(self):
        try:
            followers = self._user.users.getFollowers(user_id=self._id, fields='domain,sex,bdate,country', v='5.65')
        except:
            followers = None

        sleep(self._timeout)
        return followers

    def userPhotos(self):
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
                    photo['likes'] = self._user.likes.getList(type=photo, owner_id=self._id, item_id=photo_id,
                                                              filter=likes, extended=1, v='5.65')
                except:
                    photo['likes'] = None

                sleep(self._timeout)

                try:
                    photo['comments'] = self._user.photos.getComments(owner_id=self._id, photo_id=photo_id, extended=1,
                                                                      fields='first_name,last_name', v='5.65')
                except:
                    photo['comments'] = None

                photos['photos']['items'].append(photo)
                sleep(self._timeout)
        except:
            photos = None

        return photos

    def userWall(self):
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
                    post['likes'] = self._user.likes.getList(type=post, owner_id=self._id, item_id=post_id,
                                                             filter=likes, extended=1, v='5.65')
                except:
                    post['likes'] = None

                sleep(self._timeout)

                try:
                    post['attachments'] = item['attachments']
                except:
                    pass

                try:
                    post['comments'] = self._user.photos.getComments(owner_id=self._id, post_id=post_id, extended=1,
                                                                     fields='first_name,last_name', v='5.65')
                except:
                    post['comments'] = None

                wall['wall']['items'].append(post)
                sleep(self._timeout)
        except:
            wall = None

        return wall

    def userGroups(self):
        try:
            groups = {}
            groups['groups'] = self._user.groups.get(user_id=self._id, count=200, extended=1,
                                                     fields='id,name,screen_name', v='5.65')

            for item in groups['groups']['items']:
                item.pop('is_advertiser')
                item.pop('is_member')
                item.pop('photo_200')
                item.pop('photo_100')
                item.pop('photo_50')
        except:
            groups = None

        sleep(self._timeout)
        return groups

    def userAllInfo(self):

        info = {}
        start = clock()

        print('\nStart loading information about %s' % (self._user_name + ' ' + self._user_surname))

        info['main_info'] = self.userMainInfo()
        print('[%d s]Main information was loaded...' % (clock() - start))

        info['friends'] = self.userFriends()
        print('[%d s]Friends were loaded...' % (clock() - start))

        info['followers'] = self.userFollowers()
        print('[%d s]Followers were loaded...' % (clock() - start))

        info['groups'] = self.userGroups()
        print('[%d s]Groups were loaded...' % (clock() - start))

        info['wall'] = self.userWall()
        print('[%d s]Wallposts were loaded...' % (clock() - start))

        info['photos'] = self.userPhotos()
        print('[%d s]Photos were loaded...' % (clock() - start))

        db = GraphDatabase()
        db.addUser(info)

        print('Information about %s was successfully loaded to Graph Database' % (self._user_name + ' ' + self._user_surname))


if __name__ == '__main__':
    try:
        domain = input('Enter domain: ')
        s = VK_UserInfo(token=token, domain=domain)
        s.userAllInfo()
    except vk.exceptions.VkAPIError:
        print('Error: invalid token')
    except:
        print('Error!')

