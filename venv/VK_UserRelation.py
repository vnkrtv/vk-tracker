from VK_UserAnalizer import VK_UserAnalizer


class VK_UserRelation:
    def __init__(self, user1_domain, date1, user2_domain, date2, token):

        self._user1_id = vk.API(vk.Session(access_token=token)).users.get(user_ids=user1_domain, v='5.65')[0]['id']
        self._user2_id = vk.API(vk.Session(access_token=token)).users.get(user_ids=user2_domain, v='5.65')[0]['id']

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

