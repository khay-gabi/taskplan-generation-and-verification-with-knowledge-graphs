from neo4j import GraphDatabase

class QueryDatabase:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def queries(self, query):
        with self.driver.session() as session:
            results = session.run(query)
            records_string = ""
            for record in results:
                records_string += str(record) + "\n"
                print(records_string)
            return records_string


