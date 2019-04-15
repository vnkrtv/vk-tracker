import os
import json
import vk

from datetime import datetime as time
from tkinter import *
from time import clock, sleep
from GraphDB import GraphDB
from MongoDB import MongoDB

class VK_UserInfo:
    _timeout = 0.35

    def __init__(self, token, domain):

        self._token = token
        self._user = vk.API(vk.Session(access_token=token))

        self._id = self._user.users.get(user_ids=domain, v='5.65')[0]['id']
        self._user_name = self._user.users.get(user_ids=domain, v='5.65')[0]['first_name']
        self._user_surname = self._user.users.get(user_ids=domain, v='5.65')[0]['last_name']

    def userFirstName(self):
        return self._user_name

    def userLastName(self):
        return self._user_surname

    def userID(self):
        return self._id

    def userFolder(self):
        return self.userFirstName() + ' ' + self.userLastName() + ' [id' + str(self.userID()) + ']'

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

    def userGroups(self):
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

    def userAllInfo(self):

        info = {}
        start = clock()

        print('Start loading information about %s\n' % (self._user_name + ' ' + self._user_surname))

        info['main_info'] = self.userMainInfo()
        print('[%d s]Main information was loaded...\n' % (clock() - start))

        info['friends'] = self.userFriends()
        print('[%d s]Friends were loaded...\n' % (clock() - start))

        info['followers'] = self.userFollowers()
        print('[%d s]Followers were loaded...\n' % (clock() - start))

        info['groups'] = self.userGroups()
        print('[%d s]Groups were loaded...\n' % (clock() - start))

        info['wall'] = self.userWall()
        print('[%d s]Wallposts were loaded...\n' % (clock() - start))

        info['photos'] = self.userPhotos()
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

    """
    def saveAllInfo(self):
        info = self.userAllInfo()
        path = '../userdata/' + self.userFolder()

        if not os.path.exists(path):
            os.makedirs(path)

        date = time.now().timetuple()
        file = str(date[3]) + '.' + str(date[4]) + ' ' + str(date[2]) + '.' + str(date[1]) + '.' + str(date[0]) + '.json'

        info['date'] = {
            'year':    date[0],
            'month':   date[1],
            'day':     date[2],
            'hour':    date[3],
            'minutes': date[4]
        }

        json.dump(info, open(path + '/' + file, 'w'))

        return info
    """

    def addUserToDB(self):
        info = self.userAllInfo()

        MongoDB().addUser(info)
        GraphDB().addUser(info)

        return info




class UserInterface(Frame):

    def __init__(self, master):

        super(UserInterface, self).__init__(master)
        self.grid()
        self.create_widgets()

    def create_widgets(self):

        self.info_lbl = Label(self, text = "Enter user domain:")
        self.info_lbl.grid(row = 0, column = 0, sticky = 'W')

        self.dom_ent = Entry(self)
        self.dom_ent.grid(row = 1, columnspan = 3, sticky = 'W')

        self.submit_bttn = Button(self, text = "Download information", command = self.download)
        self.submit_bttn.grid(row = 2, column = 0, columnspan = 3, sticky = 'W')

        self.status_txt = Text(self, width = 70, height = 70, wrap = WORD)
        self.status_txt.grid(row = 3, column = 0)

    def download(self):

        self.status_txt.delete(0.0, END)

        token = open('../token/token.txt').read()
        domain = self.dom_ent.get()

        stream = self.status_txt
        stream.write = lambda message: self.status_txt.insert(0.0, message)

        s = VK_UserInfo(token=token, domain=domain)
        self.status_txt.delete(0.0, END)
        s.saveAllInfo(stream)
        """
                try:
            token = open('../token/token.txt').read()
            domain = self.dom_ent.get()

            stream = self.status_txt
            stream.write = lambda message: self.status_txt.insert(0.0, message)

            s = VK_UserInfo(token=token, domain=domain)
            self.status_txt.delete(0.0, END)
            s.userAllInfo(stream)

        except vk.exceptions.VkAPIError:
            self.status_txt.delete(0.0, END)
            self.status_txt.insert(0.0, 'Error: invalid domain')
        except:
            self.status_txt.delete(0.0, END)
            self.status_txt.insert(0.0, 'Error!')
        """




if __name__ == '__main__':
    token = open('../token/token.txt').read()
    s = VK_UserInfo(token=token, domain='n_oriharov')
    s.addUserToDB()

#python ./VKInfoSite/manage.py runserver