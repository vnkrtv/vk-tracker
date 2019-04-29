from VK_UserAnalizer import *


class VK_UserRelation:
    def __init__(self, user1_domain, date1, user2_domain, date2):

        self._user1 = MongoDB().loadUserInfo(domain=user1_domain, date=date1)
        self._user2 = MongoDB().loadUserInfo(domain=user2_domain, date=date2)

        self._user1_first_name = self._user1['main_info']['first_name']
        self._user2_first_name = self._user2['main_info']['first_name']

        self._user1_last_name = self._user1['main_info']['last_name']
        self._user2_last_name = self._user2['main_info']['last_name']

        self._user1_id = self._user1['main_info']['id']
        self._user2_id = self._user2['main_info']['id']

        self._user1_domain = user1_domain
        self._user2_domain = user2_domain


    def check_wall(self):

        user1Wall = self._user1['wall']
        user2Wall = self._user2['wall']

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

        for post in user1Wall['items']:
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

        likes_count = comm_count = 0

        for post in user2Wall['items']:
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

        user1Photos = self._user1['photos']
        user2Photos = self._user2['photos']

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

        for photo in user1Photos['items']:
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

        likes_count = comm_count = 0

        for photo in user2Photos['items']:
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

        user1Friends = self._user1['friends']
        user2Friends = self._user2['friends']

        friends, result = {}, {
            'items': []
        }

        for friend in user1Friends['items']:
            id = friend['id']
            friends[id] = friend

        for friend in user2Friends['items']:
            id = friend['id']
            if id in friends:
                friend.pop('bdate') if 'bdate' in friend else None
                result['items'].append(friend)

        result['counter'] = len(result['items'])

        return result


    def check_groups(self):

        user1Groups = self._user1['groups']
        user2Groups = self._user2['groups']

        groups, result = {}, {
            'items': []
        }

        for group in user1Groups['items']:
            id = group['id']
            groups[id] = group

        for group in user2Groups['items']:
            id = group['id']
            if id in groups:
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

        wall    = self.check_wall()
        photos  = self.check_photos()

        result['first_user2second_user'] = {
            'wall':   wall[0],
            'photos': photos[0]
        }

        result['second_user2first_user'] = {
            'wall':   wall[1],
            'photos': photos[1]
        }

        return result