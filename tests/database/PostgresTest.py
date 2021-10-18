import os
import unittest
import psycopg2 as pg
from psycopg2 import extensions

DATABASE_URL = os.environ.get('DATABASE_URL')
DATABASE_PASSWORD = os.environ.get('DATABASE_PASSWORD')


class PostgreSQLTest(unittest.TestCase):

    def connection_test(self):

        try:
            con = pg.connect(DATABASE_URL, password=DATABASE_PASSWORD)

        except pg.Error:
            con = None

        self.assertTrue(con is not None and con.status == extensions.STATUS_READY)


if __name__ == '__main__':
    unittest.main()
