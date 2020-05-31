# pylint: disable=global-statement, invalid-name, line-too-long, too-many-branches
"""Class for working with Neo4j DB without Django ORM"""
from django.conf import settings
from py2neo import Graph, Node, Relationship

_db_conn: Graph = None


def set_conn(url: str, user: str, password: str) -> None:
    """
    Establish user connection to Neo4j database

    :param url: Neo4j url
    :param user: Neo4j user
    :param password: Neo4j user password
    """
    global _db_conn
    _db_conn = Graph(url, user=user, password=password)


def get_conn() -> Graph:
    """
    Get user connection to Neo4j database

    :return: Graph - connection to database
    """
    global _db_conn
    if not _db_conn:
        set_conn(
            url=settings.DATABASES['neo4j']['URL'],
            user=settings.DATABASES['neo4j']['USER'],
            password=settings.DATABASES['neo4j']['PASSWORD'])
    return _db_conn


class Neo4jStorage:
    """Class for putting vk user info in Neo4j DB"""

    graph: Graph

    liked = Relationship.type('LIKED')
    commented = Relationship.type('COMMENTED')
    posted = Relationship.type('POSTED')
    subscribe_on = Relationship.type('SUBSCRIBE_ON')
    friend_of = Relationship.type('FRIEND_OF')
    follows = Relationship.type('FOLLOWS')

    @staticmethod
    def connect(conn: Graph):
        """
        Establish connection to Neo4jDB

        :param conn: Neo4j connection
        """
        obj = Neo4jStorage()
        obj.graph = conn
        return obj

    @staticmethod
    def parse_user_info(user: dict) -> dict:
        """
        Parse dict with user info

        :param user: <dict>
          {
            'main_info': { ... },
            'friends': { ... },
            'followers': { ... },
            'groups': { ... },
            'wall': { ... },
            'photos': { ... },
            'date': { ... }
          }
        :return: dict with user info for putting in Neo4j DB
        """
        friends = [friend['id'] for friend in user['friends']['items']]
        followers = [follower['id'] for follower in user['followers']['items']]
        groups = [group['id'] for group in user['groups']['items']]

        country = user['main_info'].get('country', None)
        country = country.get('title', '') if country else ''

        city = user['main_info'].get('city', None)
        city = city.get('title', '') if city else ''

        bday = user['main_info'].get('bdate', '')
        bday_month = user['main_info'].get('bdate', ' . . ').split('.')[1]
        bday_day = user['main_info'].get('bdate', ' . . ').split('.')[0]

        if len(bday.split('.')) == 2:
            bday_year = ''
        else:
            bday_year = user['main_info'].get('bdate', ' . . ').split('.')[2]

        return {
            'first_name': user['main_info']['first_name'],
            'last_name': user['main_info']['last_name'],
            'domain': user['main_info']['domain'],
            'id': user['main_info']['id'],
            'instagram': user['main_info'].get('instagram', ''),
            'status': user['main_info'].get('status', ''),
            'bday': bday,
            'bday_year': bday_year,
            'bday_month': bday_month,
            'bday_day': bday_day,
            'country': country,
            'city': city,
            'friends': friends,
            'followers': followers,
            'groups': groups
        }

    def add_user(self, user) -> None:
        """
        Add user to DB

        :param user: <dict>
          {
            'main_info': { ... },
            'friends': { ... },
            'followers': { ... },
            'groups': { ... },
            'wall': { ... },
            'photos': { ... },
            'date': { ... }
          }
        """

        user_info = Neo4jStorage.parse_user_info(user)
        added_user = Node('Person', **user_info)
        for person in self.graph.nodes.match('Person'):
            if person['domain'] == user_info['domain']:
                self.graph.evaluate("""

                            MATCH (n:Person) WHERE n.domain="%s"
                            OPTIONAL MATCH (n)-[l_rel:LIKED]-()
                            OPTIONAL MATCH (n)-[c_rel:COMMENTED]-()
                            OPTIONAL MATCH (n)-[sub_rel:SUBSCRIBE_ON]-()
                            OPTIONAL MATCH (n)-[post_rel:POSTED]-(posts)
                            OPTIONAL MATCH ()-[l_posts_rel:LIKED]-(posts)
                            OPTIONAL MATCH ()-[c_posts_rel:COMMENTED]-(posts)
                            OPTIONAL MATCH (n)-[fr_rel_1:FRIEND_OF]-(fr)
                            OPTIONAL MATCH (fr)-[fr_rel_2:FRIEND_OF]-(n)
                            OPTIONAL MATCH (n)-[foll_rel:FOLLOWS]-()
                            DELETE l_rel, c_rel, l_posts_rel, c_posts_rel,
                                     sub_rel, post_rel, fr_rel_1, fr_rel_2,
                                     foll_rel, posts, n
                                   
                                     """

                                    % user_info['domain'])

        self.graph.create(added_user)

        for post in self.graph.nodes.match('Post'):
            for person in self.graph.nodes.match('Person'):
                if person['id'] in post['likes']:
                    self.graph.merge(self.liked(person, post))

        for photo in self.graph.nodes.match('Photo'):
            for person in self.graph.nodes.match('Person'):
                if person['id'] in photo['likes']:
                    self.graph.merge(self.liked(person, photo))

        for post in self.graph.nodes.match('Post'):
            for person in self.graph.nodes.match('Person'):
                if person['id'] in post['comments']:
                    self.graph.merge(self.commented(person, post))

        for photo in self.graph.nodes.match('Photo'):
            for person in self.graph.nodes.match('Person'):
                if person['id'] in photo['comments']:
                    self.graph.merge(self.commented(person, photo))

        for post in user['wall']['items']:
            post_info = {
                'likes_count': post['likes']['count'],
                'post_id': post['post_id'],
                'text': post['text'],
                'comments_count': post['comments']['count'],
                'comments': [item['id'] for item in post['comments']['items']],
                'likes': [item['id'] for item in post['likes']['items']]
            }
            node = Node('Post', **post_info)

            self.graph.create(node)
            self.graph.merge(self.posted(added_user, node))

            for person in self.graph.nodes.match('Person'):
                if user_info['id'] in post_info['likes']:
                    self.graph.merge(self.liked(person, node))

            for person in self.graph.nodes.match('Person'):
                if user_info['id'] in post_info['comments']:
                    self.graph.merge(self.commented(person, node))

        for photo in user['photos']['items']:
            photo_info = {
                'likes_count': photo['likes']['count'],
                'photo_id': photo['photo_id'],
                'comments_count': photo['comments']['count'],
                'comments': [item['id'] for item in photo['comments']['items']],
                'likes': [item['id'] for item in photo['likes']['items']]
            }
            node = Node('Photo', **photo_info)

            self.graph.create(node)
            self.graph.merge(self.posted(added_user, node))

            for person in self.graph.nodes.match('Person'):
                if user_info['id'] in photo_info['likes']:
                    self.graph.merge(self.liked(person, node))

            for person in self.graph.nodes.match('Person'):
                if user_info['id'] in photo_info['comments']:
                    self.graph.merge(self.commented(person, node))

        groups_id = []
        for group in self.graph.nodes.match('Group'):
            groups_id.append(group['id'])

        for group in user['groups']['items']:
            if group['id'] not in groups_id:
                node = Node('Group', **group)
                self.graph.create(node)

        for group in self.graph.nodes.match('Group'):
            _id = group['id']
            for person in self.graph.nodes.match('Person'):
                if _id in person['groups']:
                    self.graph.merge(self.subscribe_on(person, group))

        for person in self.graph.nodes.match('Person'):
            if (user_info['id'] in person['friends']) or (person['id'] in user_info['friends']):
                self.graph.merge(self.friend_of(person, added_user) | self.friend_of(added_user, person))

        for person in self.graph.nodes.match('Person'):
            if user_info['id'] in person['followers']:
                self.graph.merge(self.follows(added_user, person))
            elif person['id'] in user_info['followers']:
                self.graph.merge(self.follows(person, added_user))
