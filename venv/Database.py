from neo4j import GraphDatabase


class Database(object):

    def __init__(self, uri, user, password):
        self._driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self._driver.close()

    def print_greeting(self, user):
        with self._driver.session() as session:
            session.write_transaction(self.addUser, user)

    @staticmethod
    def addUser(tx, user):

        user['first_name'] = user['main_info']['first_name']
        user['last_name']  = user['main_info']['last_name']
        user['id']         = user['main_info']['id']

        tx.run(
            """
            CREATE (
                {id}:User {
                            first_name: {first_name},
                            last_name:  {last_name},
                            main_info:  {main_info},
                            friends:    {friends},
                            followers:  {followers},
                            groups:     {groups},
                            wall:       {wall},
                            photos:     {photos}
                        }                                       
                )
            """.format(**user)
        )


