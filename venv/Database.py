from py2neo import Graph, Node, Relationship


class GraphDatabase(object):

    def __init__(self, url="bolt://localhost:7687", user='neo4j', password='admin'):
        self._graph = Graph(url, user=user, password=password)

    def getGraph(self):
        return self._graph

    def addUser(self, user):

        friends, groups = [], []

        for friend in user['friends']['items']:
            friends.append(friend['id'])

        for group in user['groups']['items']:
            groups.append(group['id'])

        user_info = {
            'first_name': user['main_info']['first_name'],
            'last_name':  user['main_info']['last_name'],
            'domain':     user['main_info']['domain'],
            'id':         user['main_info']['id'],
            'friends':    friends,
            'groups':     groups
        }

        added_user = Node('Person', **user_info)
        self._graph.create(added_user)


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