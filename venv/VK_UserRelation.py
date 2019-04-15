from VK_UserAnalizer import VK_UserAnalizer


class VK_UserRelation:
    def __init__(self, user1_domain, date1, user2_domain, date2, token):

        first_user  = vk.API(vk.Session(access_token=token)).users.get(user_ids=user1_domain, v='5.65')
        second_user = vk.API(vk.Session(access_token=token)).users.get(user_ids=user2_domain, v='5.65')

        self._user1_id = first_user[0]['id']
        self._user1_first_name = first_user[0]['first_name']
        self._user1_last_name = first_user[0]['last_name']

        self._user2_id = second_user[0]['id']
        self._user2_first_name = second_user[0]['first_name']
        self._user2_last_name = second_user[0]['last_name']

        pass


    def __init__(self, user1, user2):

        self._user1 = user1
        self._user2 = user2


    def checkWall(self):

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
                    result[0]['comments']['items'].append(comm)
                    comm_count += 1

        result[0]['likes']['counter'] = likes_count
        result[0]['comments']['counter'] = comm_count

        return result


    def checkPhotos(self):

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

            for comm in post['comments']['items']:
                if comm['from_id'] == self._user1_id:
                    comm.pop('from_id')
                    result[0]['comments']['items'].append(comm)
                    comm_count += 1

        result[0]['likes']['counter'] = likes_count
        result[0]['comments']['counter'] = comm_count

        return result


    def checkFriends(self):

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
                friend.pop('bdate')
                friend.pop('bdate')
                friend.pop('bdate')
                result['items'].append(friend)

        result['counter'] = len(result['items'])

        return result


    def checkGroups(self):

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
                groups['items'].append(group)

        result['counter'] = len(result['items'])

        return result


    def getActivity(self):

        result = {
            'user1_info': {
                'first_name': self._user1_first_name,
                'last_name':  self._user1_last_name,
                'id':         self._user1_id
            },
            'user2_info': {
                'first_name': self._user2_first_name,
                'last_name':  self._user2_last_name,
                'id':         self._user2_id
            },
            'mutual_friends': self.checkFriends(),
            'mutual_groups':  self.checkGroups()
        }

        wall    = self.checkWall()
        photos  = self.checkPhotos()

        result['user_1->user_2'] = {
            'wall':   wall[0],
            'photos': photos[0]
        }

        result['user_2->user_1'] = {
            'wall':   wall[1],
            'photos': photos[1]
        }

        return result



