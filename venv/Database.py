from neo4j import GraphDatabase


class Database(object):

    def __init__(self, uri, user, password):
        self._driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self._driver.close()

    def print_greeting(self, message):
        with self._driver.session() as session:
            greeting = session.write_transaction(self.addUser, message)
            print(greeting)

    @staticmethod
    def addUser(tx, user):
        name = user['main_info']['first_name'] + ' ' + user['main_info']['last_name']


        result = tx.run(
            "CREATE (user:%s) {" % (name,  )


