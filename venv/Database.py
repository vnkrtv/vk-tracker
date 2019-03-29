from py2neo import Graph, Node, Relationship


class GraphDatabase(object):

    def __init__(self, url="bolt://localhost:11001", user='neo4j', password='admin'):
        self._graph = Graph(url, user=user, password=password)

    def getGraph(self):
        return self._graph

    def addUser(self, user):

        friends, followers, groups = [], [], []

        for friend in user['friends']['items']:
            friends.append(friend['id'])

        for follower in user['followers']['items']:
            followers.append(follower['id'])

        for group in user['groups']['items']:
            groups.append(group['id'])

        country = user['main_info'].get('country', None)
        country = country.get('title', '') if country != None else ''

        city = user['main_info'].get('city', None)
        city = city.get('title', '') if city != None else ''

        bday       = user['main_info'].get('bdate', '')
        bday_month = user['main_info'].get('bdate', ' . . ').split('.')[1],
        bday_day   = user['main_info'].get('bdate', ' . . ').split('.')[0],
        try:
            bday_year = user['main_info'].get('bdate', ' . . ').split('.')[2]
        except:
            bday_year = 0

        user_info = {
            'first_name': user['main_info']['first_name'],
            'last_name':  user['main_info']['last_name'],
            'domain':     user['main_info']['domain'],
            'id':         user['main_info']['id'],
            'instagram':  user['main_info'].get('instagram', ''),
            'status':     user['main_info'].get('status', ''),
            'bday':       bday,
            'bday_year':  bday_year,
            'bday_month': bday_month,
            'bday_day':   bday_day,
            'country':    country,
            'city':       city,
            'friends':    friends,
            'followers':  followers,
            'groups':     groups
        }


        added_user = Node('Person', **user_info)
        userExist = False
        for person in self._graph.nodes.match('Person'):
            if person['domain'] == user_info['domain']:
                userExist = True

        if not userExist:
            self._graph.create(added_user)

        #TODO: проверить, существуют ли связи или нет
        LIKED  = Relationship.type('LIKED')

        for post in self._graph.nodes.match('Post'):
            for person in self._graph.nodes.match('Person'):
                if person['id'] in post['likes']:
                    self._graph.merge(LIKED(person, post))

        for photo in self._graph.nodes.match('Photo'):
            for person in self._graph.nodes.match('Person'):
                if person['id'] in photo['likes']:
                    self._graph.merge(LIKED(person, photo))


        COMMENTED = Relationship.type('COMMENTED')
        
        for post in self._graph.nodes.match('Post'):
            for person in self._graph.nodes.match('Person'):
                if person['id'] in post['comments']:
                    self._graph.merge(COMMENTED(person, post))

        for photo in self._graph.nodes.match('Photo'):
            for person in self._graph.nodes.match('Person'):
                if person['id'] in photo['comments']:
                    self._graph.merge(COMMENTED(person, photo))


        POSTED = Relationship.type('POSTED')

        for post in user['wall']['items']:
            post_info = {
                'likes_count':    post['likes']['count'],
                'post_id':        post['post_id'],
                'text':           post['text'],
                'comments_count': post['comments']['count'],
                'comments': [item['id'] for item in post['comments']['items']],
                'likes':    [item['id'] for item in post['likes']['items']]
            }
            node = Node('Post', **post_info)

            self._graph.create(node)
            self._graph.merge(POSTED(added_user, node))

            for person in self._graph.nodes.match('Person'):
                id = person['id']
                if user_info['id'] in post_info['likes']:
                    self._graph.merge(LIKED(person, node))

            for person in self._graph.nodes.match('Person'):
                id = person['id']
                if user_info['id'] in post_info['comments']:
                    self._graph.merge(COMMENTED(person, node))


        for photo in user['photos']['items']:
            photo_info = {
                'likes_count':    photo['likes']['count'],
                'photo_id':       photo['photo_id'],
                'comments_count': photo['comments']['count'],
                'comments': [item['id'] for item in photo['comments']['items']],
                'likes':    [item['id'] for item in photo['likes']['items']]
            }
            node = Node('Photo', **photo_info)

            self._graph.create(node)
            self._graph.merge(POSTED(added_user, node))

            for person in self._graph.nodes.match('Person'):
                id = person['id']
                if user_info['id'] in photo_info['likes']:
                    self._graph.merge(LIKED(person, node))

            for person in self._graph.nodes.match('Person'):
                id = person['id']
                if user_info['id'] in photo_info['comments']:
                    self._graph.merge(COMMENTED(person, node))


        SUBSCRIBE_ON = Relationship.type('SUBSCRIBE_ON')

        groups_id = []
        for group in self._graph.nodes.match('Group'):
            groups_id.append(group['id'])

        for group in user['groups']['items']:
            if group['id'] not in groups_id:
                node = Node('Group', **group)
                self._graph.create(node)

        for group in self._graph.nodes.match('Group'):
            id = group['id']
            for person in self._graph.nodes.match('Person'):
                if id in person['groups']:
                    self._graph.merge(SUBSCRIBE_ON(person, group))


        FRIEND_OF = Relationship.type('FRIEND_OF')

        for person in self._graph.nodes.match('Person'):
            id = person['id']
            if user_info['id'] in person['friends']:
                self._graph.merge(FRIEND_OF(person, added_user) | FRIEND_OF(added_user, person))


        FOLLOWS = Relationship.type('FOLLOWS')

        for person in self._graph.nodes.match('Person'):
            id = person['id']
            if user_info['id'] in person['followers']:
                self._graph.merge(FOLLOWS(added_user, person))
