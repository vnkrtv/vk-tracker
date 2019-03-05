from py2neo import Graph, Node, Relationship

class GraphDatabase(object):

    def __init__(self, url="bolt://localhost:7687", user='neo4j', password='admin'):
        self._graph = Graph(url, user=user, password=password)

    def getGraph(self):
        return self._graph

    def addUser(self, user):

        user_info = {
            'first_name': user['main_info']['first_name'],
            'last_name':  user['main_info']['last_name'],
            'domain':     user['main_info']['domain'],
            'id':         user['main_info']['id']
        }

        person = Node('Person', **user_info)
        self._graph.create(person)
