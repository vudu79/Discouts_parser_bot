import psycopg2, os
from contextlib import closing
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from config import *


class DBase:
    def __init__(self):
        self.hostname = HOST
        self.username = USER
        self.password = PASSWORD
        self.database = DBNAME
        try:
            # self.connect = psycopg2.connect(host=self.hostname, user=self.username, password=self.password,
            #                                 dbname=self.database)

            self.connect = psycopg2.connect(os.getenv("DATABASE_URL"))

            self.cursor = self.connect.cursor()
            self.cursor.execute("SELECT version();")
            record = self.cursor.fetchone()

            print("Вы подключены к - ", record, "\n")

            self.cursor.execute('CREATE TABLE IF NOT EXISTS all_gifs(id INTEGER PRIMARY KEY, tag TEXT, url TEXT)')

        except (Exception) as error:
            print("Ошибка при работе с PostgreSQL", error)

    def save_gif(self, url):
        with closing(self.connect) as c:
            with c.cursor() as cur:
                cur.execute('INSERT INTO all_gifs values (?,?)', "None", url)

    def insertTrans(self, trans_name, url_name):
        pass

#
# def db_conn():
#     try:
#         global connection
#         connection = psycopg2.connect(dbname=DBNAME, user=USER, password=PASSWORD, host=HOST)
#         connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
#         cursor = connection.cursor()
#         cursor.execute("SELECT version();")
#         record = cursor.fetchone()
#         print("Вы подключены к - ", record, "\n")
#         return connection
#     except (Exception, Error) as error:
#         print("Ошибка при работе с PostgreSQL", error)
#         return None
#
#
# def create_tables():
#     with closing(connection) as c:
#         with c.cursor() as cur:
#             cur.execute('CREATE TABLE IF NOT EXISTS all_gifs(id INTEGER PRIMARY KEY, tag TEXT, url TEXT)')
#
#
# def save_gif(url):
#     with closing(connection) as c:
#         with c.cursor() as cur:
#             cur.execute('INSERT INTO all_gifs values (?,?)', "None", url)
