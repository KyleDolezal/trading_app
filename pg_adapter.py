import psycopg2
import psycopg2.pool
import os
import logging
logger = logging.getLogger(__name__)

class PG_Adapter:
    def __init__(self):
        pool = psycopg2.pool.SimpleConnectionPool(
                2, 3, user=os.getenv('PYWAY_DATABASE_USERNAME'), password=os.getenv('PYWAY_DATABASE_PASSWORD'),
                host='localhost', port='5432', database=os.getenv('PYWAY_DATABASE_NAME'))
        self.connection = pool.getconn()
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