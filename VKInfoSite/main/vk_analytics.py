class VKAnalyzer:

    def __init__(self, old_info: dict, new_info: dict):
        self._old_info = old_info
        self._new_info = new_info
        self.check_dates(
            date1=old_info['date'],
            date2=new_info['date'])

    def check_dates(self, date1, date2):

        def swap_info():
            self._old_info, self._new_info = self._new_info, self._old_info

        def parse_date(date):
            date_tuple = tuple(map(int, date.replace(' ', '-').split('-')))
            return {
                'year': date_tuple[4],
                'month': date_tuple[3],
                'date': date_tuple[2],
                'hour': date_tuple[1],
                'min': date_tuple[1]
            }
        date1 = parse_date(date1)
        date2 = parse_date(date2)
        if date1['year'] >= date2['year']:
            swap_info()
        else:
            if date1['month'] >= date2['month']:
                swap_info()
            else:
                if date1['date'] >= date2['date']:
                    swap_info()
                else:
                    if date1['hour'] >= date2['hour']:
                        swap_info()
                    else:
                        if date1['min'] >= date2['min']:
                            swap_info()

    def cmp_main_info(self):
        old_main = self._old_info['main_info']
        new_main = self._new_info['main_info']
        cmp_dict = {}
        for old_key in old_main:
            if new_main.get(old_key):
                if old_main[old_key] != new_main[old_key]:
                    if isinstance(old_main[old_key], dict) and isinstance(new_main[old_key], dict):
                        for key in old_main[old_key]:
                            if new_main[old_key].get(key):
                                if not isinstance(old_main[old_key], dict) and not isinstance(new_main[old_key], dict):
                                    cmp_dict[old_main[old_key][key]] = {
                                        'old': old_main[old_key][key],
                                        'new': new_main[old_key][key]
                                    }
                    else:
                        cmp_dict[old_key] = {
                            'old': old_main[old_key],
                            'new': new_main[old_key]
                        }
        return cmp_dict

    def cmp_friends(self):
        old_friends = self._old_info['friends']['items']
        new_friends = self._new_info['friends']['items']
        cmp_dict = {}
        for friend in old_friends:
            _id = friend['id']
            cmp_dict[_id] = [friend, 0]

        for friend in new_friends:
            _id = friend['id']
            if _id in cmp_dict:
                cmp_dict.pop(_id)
            else:
                cmp_dict[_id] = [friend, 1]
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
            _id = follower['id']
            cmp_dict[_id] = [follower, 0]
        for follower in new_followers:
            _id = follower['id']

            if _id in cmp_dict:
                cmp_dict.pop(_id)
            else:
                cmp_dict[_id] = [follower, 1]
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

    def cmp_groups(self):
        old_groups = self._old_info['groups']['items']
        new_groups = self._new_info['groups']['items']
        cmp_dict = {}
        for group in old_groups:
            _id = group['id']
            cmp_dict[_id] = [group, 0]

        for group in new_groups:
            _id = group['id']
            if _id in cmp_dict:
                cmp_dict.pop(_id)
            else:
                cmp_dict[_id] = [group, 1]
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
            _id = photo['photo_id']
            old_ph_dict[_id] = [photo['comments'], photo['likes']]
        for photo in new_photos:
            _id = photo['photo_id']
            new_ph_dict[_id] = [photo['comments'], photo['likes']]
        list_ids = []
        changes_dict = {
            'new': [],
            'deleted': [],
            'items': []
        }
        for _id in old_ph_dict:
            if _id not in new_ph_dict:
                old_ph = {
                    'photo_id': _id,
                    'comments': old_ph_dict[_id][0],
                    'likes':    old_ph_dict[_id][1],
                }
                changes_dict['deleted'].append(old_ph)
                list_ids.append(_id)
        for _id in list_ids:
            old_ph_dict.pop(_id)
        list_ids = []
        for _id in new_ph_dict:
            if _id not in old_ph_dict:
                new_ph = {
                    'photo_id': _id,
                    'comments': new_ph_dict[_id][0],
                    'likes':    new_ph_dict[_id][1],
                }
                changes_dict['new'].append(new_ph)
                list_ids.append(_id)
        for _id in list_ids:
            new_ph_dict.pop(_id)
        for (old, new) in zip(old_ph_dict, new_ph_dict):
            changes_comm_list, changes_likes_list = [], []
            old_comm = old_ph_dict[old][0]
            new_comm = new_ph_dict[new][0]
            if old_comm != new_comm:
                cmp_dict = {}

                for item in old_comm['items']:
                    _id = item['id']
                    cmp_dict[_id] = [item, 0]

                for item in new_comm['items']:
                    _id = item['id']

                    if _id in cmp_dict:
                        cmp_dict.pop(_id)
                    else:
                        cmp_dict[_id] = [item, 1]

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
                    _id = item['id']
                    cmp_dict[_id] = [item, 0]

                for item in new_likes['items']:
                    _id = item['id']

                    if _id in cmp_dict:
                        cmp_dict.pop(_id)
                    else:
                        cmp_dict[_id] = [item, 1]

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
            _id = post['post_id']

            text_dict[_id] = [post['text'], None]
            old_wall_dict[_id] = [post['comments'], post['likes']]

        for post in new_wall:
            _id = post['post_id']

            text_dict[_id] = [None, post['text']]
            new_wall_dict[_id] = [post['comments'], post['likes']]

        list_ids = []
        changes_dict = {
            'new': [],
            'deleted': [],
            'items': []
        }

        for _id in old_wall_dict:
            if _id not in new_wall_dict:
                old_post = {
                    'post_id': _id,
                    'text': text_dict[_id][0],
                    'comments': old_wall_dict[_id][0],
                    'likes': old_wall_dict[_id][1],
                }

                changes_dict['deleted'].append(old_post)
                list_ids.append(_id)

        for _id in list_ids:
            old_wall_dict.pop(_id)
            text_dict.pop(_id)

        list_ids = []

        for _id in new_wall_dict:
            if _id not in old_wall_dict:
                new_post = {
                    'post_id': _id,
                    'text': text_dict[_id][1],
                    'comments': new_wall_dict[_id][0],
                    'likes': new_wall_dict[_id][1],
                }

                changes_dict['new'].append(new_post)
                list_ids.append(_id)

        for _id in list_ids:
            new_wall_dict.pop(_id)
            text_dict.pop(_id)

        for (old, new) in zip(old_wall_dict, new_wall_dict):
            changes_likes_list, change_comm_list = [], []

            old_comm = old_wall_dict[old][0]
            new_comm = new_wall_dict[new][0]

            cmp_dict = {}

            for item in old_comm['items']:
                _id = item['id']
                cmp_dict[_id] = [item, 0]

            for item in new_comm['items']:
                _id = item['id']

                if _id in cmp_dict:
                    cmp_dict.pop(_id)
                else:
                    cmp_dict[_id] = [item, 1]

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
                _id = item['id']
                cmp_dict[_id] = [item, 0]

            for item in new_likes['items']:
                _id = item['id']

                if _id in cmp_dict:
                    cmp_dict.pop(_id)
                else:
                    cmp_dict[_id] = [item, 1]

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
            'fullname':  self._new_info['main_info']['first_name'] + ' ' + self._new_info['main_info']['last_name']
        }

        return changes_dict


class VKRelation:

    def __init__(self, user1_info: dict, user2_info: dict):
        self._user1 = user1_info
        self._user2 = user2_info

        self._user1_first_name = self._user1['main_info']['first_name']
        self._user2_first_name = self._user2['main_info']['first_name']

        self._user1_last_name = self._user1['main_info']['last_name']
        self._user2_last_name = self._user2['main_info']['last_name']

        self._user1_id = self._user1['main_info']['id']
        self._user2_id = self._user2['main_info']['id']

        self._user1_domain = self._user1['main_info']['domain']
        self._user2_domain = self._user2['main_info']['domain']

    def check_wall(self):
        user1_wall = self._user1['wall']
        user2_wall = self._user2['wall']
        result = [{
            'likes': {
                'items': []
            },
            'comments': {
                'items': []
            }
        }, {
            'likes': {
                'items': []
            },
            'comments': {
                'items': []
            }
        }]
        likes_count, comm_count = 0, 0

        for post in user1_wall['items']:
            post_id = post['post_id']

            for like in post['likes']['items']:
                if like['id'] == self._user2_id:
                    d = {
                        'post_id': post_id
                    }
                    result[1]['likes']['items'].append(d)
                    likes_count += 1

            for comm in post['comments']['items']:
                if comm['from_id'] == self._user2_id:
                    comm.pop('from_id')
                    comm['post_id'] = post_id
                    result[1]['comments']['items'].append(comm)
                    comm_count += 1

        result[1]['likes']['counter'] = likes_count
        result[1]['comments']['counter'] = comm_count

        likes_count, comm_count = 0, 0

        for post in user2_wall['items']:
            post_id = post['post_id']

            for like in post['likes']['items']:
                if like['id'] == self._user1_id:
                    d = {
                        'post_id': post_id
                    }
                    result[0]['likes']['items'].append(d)
                    likes_count += 1

            for comm in post['comments']['items']:
                if comm['from_id'] == self._user1_id:
                    comm.pop('from_id')
                    comm['post_id'] = post_id
                    result[0]['comments']['items'].append(comm)
                    comm_count += 1

        result[0]['likes']['counter'] = likes_count
        result[0]['comments']['counter'] = comm_count
        return result

    def check_photos(self):
        user1_photos = self._user1['photos']
        user2_photos = self._user2['photos']
        result = [{
            'likes': {
                'items': []
            },
            'comments': {
                'items': []
            }
        }, {
            'likes': {
                'items': []
            },
            'comments': {
                'items': []
            }
        }]
        likes_count = comm_count = 0

        for photo in user1_photos['items']:
            photo_id = photo['photo_id']

            for like in photo['likes']['items']:
                if like['id'] == self._user2_id:
                    d = {
                        'photo_id': photo_id
                    }
                    result[1]['likes']['items'].append(d)
                    likes_count += 1

            for comm in photo['comments']['items']:
                if comm['from_id'] == self._user2_id:
                    comm.pop('from_id')
                    comm['photo_id'] = photo_id
                    result[1]['comments']['items'].append(comm)
                    comm_count += 1

        result[1]['likes']['counter'] = likes_count
        result[1]['comments']['counter'] = comm_count

        likes_count, comm_count = 0, 0

        for photo in user2_photos['items']:
            photo_id = photo['photo_id']

            for like in photo['likes']['items']:
                if like['id'] == self._user1_id:
                    d = {
                        'photo_id': photo_id
                    }
                    result[0]['likes']['items'].append(d)
                    likes_count += 1

            for comm in photo['comments']['items']:
                if comm['from_id'] == self._user1_id:
                    comm.pop('from_id')
                    comm['photo_id'] = photo_id
                    result[0]['comments']['items'].append(comm)
                    comm_count += 1

        result[0]['likes']['counter'] = likes_count
        result[0]['comments']['counter'] = comm_count
        return result

    def check_friends(self):
        user1_friends = self._user1['friends']
        user2_friends = self._user2['friends']
        friends, result = {}, {
            'items': []
        }
        for friend in user1_friends['items']:
            _id = friend['id']
            friends[_id] = friend

        for friend in user2_friends['items']:
            _id = friend['id']
            if _id in friends:
                friend.pop('bdate') if 'bdate' in friend else None
                result['items'].append(friend)

        result['counter'] = len(result['items'])
        return result

    def check_groups(self):
        user1_groups = self._user1['groups']
        user2_groups = self._user2['groups']
        groups, result = {}, {
            'items': []
        }
        for group in user1_groups['items']:
            _id = group['id']
            groups[_id] = group
        for group in user2_groups['items']:
            _id = group['id']
            if _id in groups:
                result['items'].append(group)
        result['counter'] = len(result['items'])
        return result

    def get_mutual_activity(self):
        result = {
            'user1_info': {
                'first_name': self._user1_first_name,
                'last_name':  self._user1_last_name,
                'domain':     self._user1_domain,
                'id':         self._user1_id
            },
            'user2_info': {
                'first_name': self._user2_first_name,
                'last_name':  self._user2_last_name,
                'domain':     self._user2_domain,
                'id':         self._user2_id
            },
            'mutual_friends': self.check_friends(),
            'mutual_groups':  self.check_groups()
        }
        wall = self.check_wall()
        photos = self.check_photos()

        result['first_user2second_user'] = {
            'wall':   wall[0],
            'photos': photos[0]
        }

        result['second_user2first_user'] = {
            'wall':   wall[1],
            'photos': photos[1]
        }
        return result
