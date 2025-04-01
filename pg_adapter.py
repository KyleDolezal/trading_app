import psycopg2
import os

class PG_Adapter:
    def __init__(self):
        self.connection = psycopg2.connect(database=os.getenv('PYWAY_DATABASE_NAME'), user=os.getenv('PYWAY_DATABASE_USERNAME'), password=os.getenv('PYWAY_DATABASE_PASSWORD'), host="localhost", port=5432)
        self.connection.autocommit = True
        self.cursor = self.connection.cursor()

    def exec_query(self, query):
        self.cursor.execute(query)
        record = None
        try:
            record = self.cursor.fetchall()
        except:
            pass

        return record