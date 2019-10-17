from VK_UserInfo import *

class VK_UserAnalizer:

    def __init__(self, domain, date1, date2, mongo_host, mongo_port):

        mdb = VKMongoDB(host=mongo_host, port=mongo_port)
        if not mdb.check_domain(domain):
            raise Exception('No user with input domain in base')

        self._new_info = mdb.load_user_info(domain=domain, date=date2)
        self._old_info = mdb.load_user_info(domain=domain, date=date1)

        #self.check_dates(date1, date2);


    def check_dates(self, date1, date2):
        #"{hour:02}-{minutes:02} {day}-{month:02}-{year}".format(**user['date'])
        date1 = tuple(map(int, date1.replace(' ', '-').split('-')))
        date2 = tuple(map(int, date2.replace(' ', '-').split('-')))

        for i in range(4, 1, -1):
            if date1[i] != date2[i]:
                if date2[i] > date1[i]:
                    buff_dict    = self._new_info
                    self._new_info = self._old_info
                    self._old_info = buff_dict
                    return

        for i in range(0, 2):
            if date1[i] != date2[i]:
                if date2[i] > date1[i]:
                    buff_dict    = self._new_info
                    self._new_info = self._old_info
                    self._old_info = buff_dict
                    return


    def cmp_main_info(self):
        old_main = self._old_info['main_info']
        new_main = self._new_info['main_info']

        cmp_dict = {}

        for (old, new) in zip(old_main, new_main):
            if old_main[old] != new_main[new]:
                if type(old_main[old]) is not dict:
                    cmp_dict[old] = {
                        'old': old_main[old],
                        'new': new_main[new]
                    }

        return cmp_dict


    def cmp_friends(self):
        old_friends = self._old_info['friends']['items']
        new_friends = self._new_info['friends']['items']

        cmp_dict = {}

        for friend in old_friends:
            id = friend['id']
            cmp_dict[id] = [friend, 0]

        for friend in new_friends:
            id = friend['id']

            if id in cmp_dict:
                cmp_dict.pop(id)
            else:
                cmp_dict[id] = [friend, 1]

        changes_dict = {
            'new': [],
            'deleted': []
        }

        for item in cmp_dict:
            if cmp_dict[item][1]:
                changes_dict['new'].append(cmp_dict[item][0])
            else:
                changes_dict['deleted'].append(cmp_dict[item][0])

        return changes_dict


    def cmp_followers(self):
        old_followers = self._old_info['followers']['items']
        new_followers = self._new_info['followers']['items']

        cmp_dict = {}

        for follower in old_followers:
            id = follower['id']
            cmp_dict[id] = [follower, 0]

        for follower in new_followers:
            id = follower['id']

            if id in cmp_dict:
                cmp_dict.pop(id)
            else:
                cmp_dict[id] = [follower, 1]

        changes_dict = {
            'new': [],
            'deleted': []
        }

        for item in cmp_dict:
            if cmpDict[item][1]:
                changes_dict['new'].append(cmp_dict[item][0])
            else:
                changes_dict['deleted'].append(cmp_dict[item][0])

        return changes_dict


    def cmp_groups(self):
        old_groups = self._old_info['groups']['items']
        new_groups = self._new_info['groups']['items']

        cmp_dict = {}

        for group in old_groups:
            id = group['id']
            cmp_dict[id] = [group, 0]

        for group in new_groups:
            id = group['id']

            if id in cmp_dict:
                cmp_dict.pop(id)
            else:
                cmp_dict[id] = [group, 1]

        changes_dict = {
            'new': [],
            'deleted': []
        }

        for item in cmp_dict:
            if cmp_dict[item][1]:
                changes_dict['new'].append(cmp_dict[item][0])
            else:
                changes_dict['deleted'].append(cmp_dict[item][0])

        return changes_dict


    def cmp_photos(self):
        old_photos = self._old_info['photos']['items']
        new_photos = self._new_info['photos']['items']

        old_ph_dict, new_ph_dict = {}, {}

        for photo in old_photos:
            id = photo['photo_id']
            old_ph_dict[id] = [photo['comments'], photo['likes']]

        for photo in new_photos:
            id = photo['photo_id']
            new_ph_dict[id] = [photo['comments'], photo['likes']]

        list_ids = []
        changes_dict = {
            'new': [],
            'deleted': [],
            'items': []
        }

        for id in old_ph_dict:
            if id not in new_ph_dict:

                old_ph = {
                    'photo_id': id,
                    'comments': old_ph_dict[id][0],
                    'likes':    old_ph_dict[id][1],
                }

                changes_dict['deleted'].append(old_ph)
                list_ids.append(id)

        for id in list_ids:
            old_ph_dict.pop(id)

        list_ids = []

        for id in new_ph_dict:
            if id not in old_ph_dict:

                new_ph = {
                    'photo_id': id,
                    'comments': new_ph_dict[id][0],
                    'likes':    new_ph_dict[id][1],
                }

                changes_dict['new'].append(new_ph)
                list_ids.append(id)

        for id in list_ids:
            new_ph_dict.pop(id)

        for (old, new) in zip(old_ph_dict, new_ph_dict):
            changes_comm_list, changes_likes_list = [], []

            old_comm = old_ph_dict[old][0]
            new_comm = new_ph_dict[new][0]

            if old_comm != new_comm:
                cmp_dict = {}

                for item in old_comm['items']:
                    id = item['id']
                    cmp_dict[id] = [item, 0]

                for item in new_comm['items']:
                    id = item['id']

                    if id in cmp_dict:
                        cmp_dict.pop(id)
                    else:
                        cmp_dict[id] = [item, 1]

                for key in cmp_dict:

                    if cmp_dict[key][1]:
                        cmp_dict[key][0]['status'] = 1  # 'new comment'
                    else:
                        cmp_dict[key][0]['status'] = 0  # 'deleted comment'

                    changes_comm_list.append(cmp_dict[key][0])

            old_likes = old_ph_dict[old][1]
            new_likes = new_ph_dict[new][1]

            if old_likes != new_likes:
                cmp_dict = {}

                for item in old_likes['items']:
                    id = item['id']
                    cmp_dict[id] = [item, 0]

                for item in new_likes['items']:
                    id = item['id']

                    if id in cmp_dict:
                        cmp_dict.pop(id)
                    else:
                        cmp_dict[id] = [item, 1]

                for key in cmp_dict:

                    if cmp_dict[key][1]:
                        cmp_dict[key][0]['status'] = 1  # 'new like'
                    else:
                        cmp_dict[key][0]['status'] = 0  # 'deleted like'

                    changes_likes_list.append(cmp_dict[key][0])

            photo = {
                'comments': [],
                'likes': [],
            }
            if changes_comm_list:
                photo['comments'] = changes_comm_list
            if changes_likes_list:
                photo['likes'] = changes_likes_list
            if changes_comm_list or changes_likes_list:
                photo['photo_id'] = old
                changes_dict['items'].append(photo)

        return changes_dict

    def cmp_wall(self):
        old_wall = self._old_info['wall']['items']
        new_wall = self._new_info['wall']['items']

        old_wall_dict, new_wall_dict, text_dict = {}, {}, {}

        for post in old_wall:
            id = post['post_id']

            text_dict[id] = [post['text'], None]
            old_wall_dict[id] = [post['comments'], post['likes']]

        for post in new_wall:
            id = post['post_id']

            text_dict[id] = [None, post['text']]
            new_wall_dict[id] = [post['comments'], post['likes']]

        list_ids = []
        changes_dict = {
            'new': [],
            'deleted': [],
            'items': []
        }

        for id in old_wall_dict:
            if id not in new_wall_dict:
                old_post = {
                    'post_id': id,
                    'text': text_dict[id][0],
                    'comments': old_wall_dict[id][0],
                    'likes': old_wall_dict[id][1],
                }

                changes_dict['deleted'].append(old_post)
                list_ids.append(id)

        for id in list_ids:
            old_wall_dict.pop(id)
            text_dict.pop(id)

        list_ids = []

        for id in new_wall_dict:
            if id not in old_wall_dict:
                new_post = {
                    'post_id': id,
                    'text': text_dict[id][1],
                    'comments': new_wall_dict[id][0],
                    'likes': new_wall_dict[id][1],
                }

                changes_dict['new'].append(new_post)
                list_ids.append(id)

        for id in list_ids:
            new_wall_dict.pop(id)
            text_dict.pop(id)

        for (old, new) in zip(old_wall_dict, new_wall_dict):
            changes_likes_list, change_comm_list = [], []

            old_comm = old_wall_dict[old][0]
            new_comm = new_wall_dict[new][0]

            cmp_dict = {}

            for item in old_comm['items']:
                id = item['id']
                cmp_dict[id] = [item, 0]

            for item in new_comm['items']:
                id = item['id']

                if id in cmp_dict:
                    cmp_dict.pop(id)
                else:
                    cmp_dict[id] = [item, 1]

            for key in cmp_dict:

                if cmp_dict[key][1]:
                    cmp_dict[key][0]['status'] = 1  # 'new comment'
                else:
                    cmp_dict[key][0]['status'] = 0  # 'deleted comment'

                change_comm_list.append(cmp_dict[key][0])


            old_likes = old_wall_dict[old][1]
            new_likes = new_wall_dict[new][1]

            cmp_dict = {}

            for item in old_likes['items']:
                id = item['id']
                cmp_dict[id] = [item, 0]

            for item in new_likes['items']:
                id = item['id']

                if id in cmp_dict:
                    cmp_dict.pop(id)
                else:
                    cmp_dict[id] = [item, 1]

            for key in cmp_dict:

                if cmp_dict[key][1]:
                    cmp_dict[key][0]['status'] = 1  # 'new like'
                else:
                    cmp_dict[key][0]['status'] = 0  # 'deleted like'

                changes_likes_list.append(cmp_dict[key][0])

            post = {
                'comments': [],
                'likes': [],
            }
            if change_comm_list:
                post['comments'] = change_comm_list
            if changes_likes_list:
                post['likes'] = changes_likes_list
            if change_comm_list or changes_likes_list:
                post['post_id'] = old
                changes_dict['items'].append(post)

        return changes_dict

    def get_changes(self):
        if not self._old_info or not self._new_info:
            raise ValueError('user information was not loaded')

        changes_dict = {
            'main_info': self.cmp_main_info(),
            'friends':   self.cmp_friends(),
            'followers': self.cmp_followers(),
            'groups':    self.cmp_groups(),
            'photos':    self.cmp_photos(),
            'wall':      self.cmp_wall(),
            'domain':    self._new_info['main_info']['domain'],
            'id':        self._new_info['main_info']['id'],
        }

        return changes_dict


if __name__ == '__main__':
    pass
