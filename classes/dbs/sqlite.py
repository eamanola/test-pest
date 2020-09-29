import sqlite3
from classes.db import DB


class Sqlite(DB):

    def __init__(self):
        super(Sqlite, self).__init__()
        self.conn = None

    def connect(self, database='example.db'):
        self.conn = sqlite3.connect(database)

    def close(self):
        self.conn.close()

    def create_title_to_ext_id_table(self, table):
        cur = self.conn.cursor()

        sql = """create table if not exists {} (ext_id TEXT, title TEXT,
        year INTEGER, media_type TEXT)""".format(table)
        cur.execute(sql)

        self.conn.commit()

    def populate_title_to_ext_id_table(self, table, data):
        cur = self.conn.cursor()

        sql = 'delete from {}'.format(table)
        cur.execute(sql)

        sql = 'insert into {} VALUES (?,?,?,?)'.format(table)
        cur.executemany(sql, data)

        self.conn.commit()

    def get_ext_ids(self, table, re_show_name):
        self.conn.create_function(
            'matches',
            1,
            lambda x: 1 if re_show_name.match(x) else 0
        )

        cur = self.conn.cursor()

        sql = 'SELECT * FROM {} where matches(title)'.format(table)
        cur.execute(sql)

        return cur.fetchall()

    def print_table(self, table):
        cur = self.conn.cursor()

        sql = 'SELECT * FROM {}'.format(table)
        cur.execute(sql)

        for row in cur:
            print(row)

        sql = 'select count() from {}'.format(table)
        cur.execute(sql)
        print(cur.fetchone())