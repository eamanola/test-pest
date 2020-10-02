import sqlite3
from classes.db import DB
from classes.container import MediaLibrary, Show, Season, Extra


class Sqlite(DB):

    def __init__(self):
        super(Sqlite, self).__init__()
        self.conn = None

    def connect(self, database='example.db'):
        self.conn = sqlite3.connect(database)

    def close(self):
        self.conn.close()

    def create_title_to_ext_id_table(self, table):
        self._create_table(
            table,
            "(ext_id TEXT, title TEXT, year INTEGER, media_type TEXT)"
        )

    def populate_title_to_ext_id_table(self, table, data):
        cur = self.conn.cursor()

        sql = 'delete from {}'.format(table)
        cur.execute(sql)

        sql = """insert into {} (ext_id, title, year, media_type)
            VALUES (?,?,?,?)""".format(table)
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

    def create_containers_table(self):
        self._create_table(
            "containers",
            # type: MediaLibrary|Show|Season|Extra
            # containers&media: comma separated id list
            """(
                id TEXT,
                type TEXT,
                containers TEXT,
                media TEXT,
                parent TEXT,
                path TEXT,
                show_name TEXT,
                season_number INTEGER
            )"""
        )

    def update_containers(self, containers):

        self.delete_containers(containers)

        where, ids = self._where_ids(containers)

        data = [self._get_container_data(c) for c in containers]

        cur = self.conn.cursor()

        sql = """INSERT INTO containers (
            id,
            type,
            containers,
            media,
            parent,
            path,
            show_name,
            season_number
        ) VALUES (?,?,?,?,?,?,?,?)"""

        cur.executemany(sql, data)

    def get_container(self, container):
        cur = self.conn.cursor()

        sql = "SELECT * FROM containers WHERE id=?"
        cur.execute(sql, [container.id()])

        result = cur.fetchone()

        return_obj = self._container_from_data(result)

        return return_obj

    def delete_containers(self, containers):
        where, ids = self._where_ids(containers)

        cur = self.conn.cursor()

        sql = 'DELETE FROM containers WHERE {}'.format(where)
        cur.execute(sql, ids)

        self.conn.commit()

    def print_table(self, table):
        cur = self.conn.cursor()

        sql = 'SELECT * FROM {}'.format(table)
        cur.execute(sql)

        for row in cur:
            print(row)

        sql = 'select count() from {}'.format(table)
        cur.execute(sql)
        print(cur.fetchone())

    def _create_table(self, table, schema):
        cur = self.conn.cursor()

        sql = "CREATE TABLE IF NOT EXISTS {} {}".format(table, schema)

        cur.execute(sql)

        self.conn.commit()

    def _where_ids(self, containers, and_or='OR'):
        ids = []
        where = ""

        for container in containers:
            ids.append(container.id())
            where = '{}id=? {} '.format(where, and_or)

        where = where.rstrip('{} '.format(and_or))

        return where, ids

    def _get_container_data(self, container):

        return (
            container.id(),
            container.__class__.__name__,
            ','.join([c.id() for c in container.containers]),
            ','.join([m.id() for m in container.media]),
            container.parent().id() if container.parent() else None,
            container.path(),
            container.show_name() if hasattr(container, 'show_name') else None,
            (
                container.season_number()
                if hasattr(container, 'season_number')
                else 0
            )
        )

    def _get_container_parent(self, result):
        cur = self.conn.cursor()

        sql = "SELECT * FROM containers WHERE id=?"
        cur.execute(sql, [result[4]])

        result = cur.fetchone()

        parent = self._container_from_data(result, False, False)

        return parent

    def _get_container_children(self, result):
        containers = []
        media = []

        if result[2]:
            container_ids = result[2].split(",")
            where = ""
            for container in container_ids:
                if container.strip():
                    where = "{}id=? OR ".format(where)

            where = where.rstrip(" OR ")

            cur = self.conn.cursor()

            sql = "SELECT * FROM containers WHERE {}".format(where)
            cur.execute(sql, container_ids)

            for result in cur.fetchall():
                containers.append(self._container_from_data(
                    result,
                    False,
                    False
                ))

        if result[3]:
            # TODO:
            pass

        return containers, media

    def _container_from_data(self, result, get_children=True, get_parent=True):
        if get_parent and result[4]:
            parent = self._get_container_parent(result)
        else:
            parent = None

        if result[1] == 'MediaLibrary':
            return_obj = MediaLibrary(result[5], parent=parent)
        elif result[1] == 'Show':
            return_obj = Show(result[5], result[6], parent=parent)
        elif result[1] == 'Season':
            return_obj = Season(result[5], result[6], result[7], parent=parent)
        elif result[1] == 'Extra':
            return_obj = Extra(result[5], result[6], result[7], parent=parent)
        else:
            print('hmm hmm')
            pass

        if get_children and (result[2] or result[3]):
            containers, media = self._get_container_children(result)
            for c in containers:
                return_obj.containers.append(c)

            for m in media:
                return_obj.media.append(m)

        return return_obj
