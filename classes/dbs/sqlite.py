import sqlite3
from classes.db import DB
from classes.container import Container, MediaLibrary, Show, Season, Extra
from classes.media import Media, Episode, Movie
from classes.identifiable import Identifiable


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
        self._create_identifiables_table()

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

        self._update_identifiables(
            [i for i in containers if isinstance(i, Identifiable)]
        )

        self.conn.commit()

    def get_container(self, container):
        if isinstance(container, Container):
            container_id = container.id()
        else:
            container_id = container

        self.conn.row_factory = sqlite3.Row
        cur = self.conn.cursor()

        sql = """
            SELECT * FROM containers
            LEFT OUTER JOIN identifiables
            ON containers.id = identifiables.id
            WHERE containers.id=?
            """
        cur.execute(sql, [container_id])

        result = cur.fetchone()
        return_obj = self._container_from_data(result) if result else None

        return return_obj

    def delete_containers(self, containers):
        if not len(containers):
            return

        where, ids = self._where_ids(containers)

        cur = self.conn.cursor()

        sql = 'DELETE FROM containers WHERE {}'.format(where)
        cur.execute(sql, ids)

        self.conn.commit()

    def create_media_table(self):
        self._create_table(
            "media",
            # type: Episode|Movie
            # subtitles: comma separated list
            # title: None for Episode
            # flags: is_oad is_ncop is_nced
            """(
                id TEXT,
                type TEXT,
                parent TEXT,
                file_path TEXT,
                subtitles TEXT,
                episode_number INTEGER,
                title TEXT,
                flags TEXT
            )"""
        )
        self._create_identifiables_table()

    def update_media(self, media):

        self.delete_media(media)

        where, ids = self._where_ids(media)

        data = [self._get_media_data(m) for m in media]

        cur = self.conn.cursor()

        sql = """INSERT INTO media (
            id,
            type,
            parent,
            file_path,
            subtitles,
            episode_number,
            title,
            flags
        ) VALUES (?,?,?,?,?,?,?,?)"""

        cur.executemany(sql, data)

        self._update_identifiables(
            [i for i in media if isinstance(i, Identifiable)]
        )

        self.conn.commit()

    def get_media(self, media):
        if isinstance(media, Media):
            media_id = media.id()
        else:
            media_id = media

        self.conn.row_factory = sqlite3.Row
        cur = self.conn.cursor()

        sql = """
            SELECT * FROM media
            LEFT OUTER JOIN identifiables
            ON media.id = identifiables.id
            WHERE media.id=?
            """
        cur.execute(sql, [media_id])

        result = cur.fetchone()

        return_obj = self._media_from_data(result) if result else None

        return return_obj

    def delete_media(self, media):
        if not len(media):
            return

        where, ids = self._where_ids(media)

        cur = self.conn.cursor()

        sql = 'DELETE FROM media WHERE {}'.format(where)
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

    def _where_ids(self, items, and_or='OR', table=''):
        ids = []
        where = ""
        table = f"{table}." if table else ""

        for item in items:
            ids.append(item.id())
            where = '{}{}id=? {} '.format(where, table, and_or)

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

    def _get_media_data(self, media):
        if isinstance(media, Episode):
            flags = "{}{}{}".format(
                1 if media.is_oad() else 0,
                1 if media.is_ncop() else 0,
                1 if media.is_nced() else 0,
            )
        else:
            flags = None

        return (
            media.id(),
            media.__class__.__name__,
            media.parent().id() if media.parent() else None,
            media.file_path(),
            ','.join(media.subtitles),
            media.episode_number() if isinstance(media, Episode) else None,
            media.title() if isinstance(media, Movie) else None,
            flags
        )

    def _get_parent(self, parent_id):
        self.conn.row_factory = sqlite3.Row
        cur = self.conn.cursor()

        sql = """
            SELECT * FROM containers
            LEFT OUTER JOIN identifiables
            ON containers.id = identifiables.id
            WHERE containers.id=?
            """
        cur.execute(sql, [parent_id])

        result = cur.fetchone()

        if result:
            parent = self._container_from_data(
                result,
                get_children=False,
                get_parent=False
            )
        else:
            parent = None

        return parent

    def _get_container_children(self, result):
        container_ids = [item for item in result[2].split(",") if item.strip()]
        media_ids = [item for item in result[3].split(",") if item.strip()]
        containers = []
        media = []

        if len(container_ids):
            where = ""
            for container_id in container_ids:
                where = "{}containers.id=? OR ".format(where)

            where = where.rstrip(" OR ")

            self.conn.row_factory = sqlite3.Row
            cur = self.conn.cursor()

            sql = """
                SELECT * FROM containers
                LEFT OUTER JOIN identifiables
                ON containers.id = identifiables.id
                WHERE {}
                """.format(where)
            cur.execute(sql, container_ids)

            for result in cur.fetchall():
                containers.append(self._container_from_data(
                    result,
                    get_children=False,
                    get_parent=False
                ))

        if len(media_ids):
            where = ""
            for media_id in media_ids:
                where = "{}media.id=? OR ".format(where)

            where = where.rstrip(" OR ")

            self.conn.row_factory = sqlite3.Row
            cur = self.conn.cursor()

            sql = """
                SELECT * FROM media
                LEFT OUTER JOIN identifiables
                ON media.id = identifiables.id
                WHERE {}
                """.format(where)
            cur.execute(sql, media_ids)

            for result in cur.fetchall():
                media.append(self._media_from_data(result))

        return containers, media

    def _container_from_data(
        self,
        result_row,
        get_children=True,
        get_parent=True
    ):
        if get_parent and result_row['parent']:
            parent = self._get_parent(result_row['parent'])
        else:
            parent = None

        if result_row['type'] == 'MediaLibrary':
            return_obj = MediaLibrary(result_row['path'], parent=parent)
        elif result_row['type'] == 'Show':
            return_obj = Show(
                result_row['path'],
                result_row['show_name'],
                parent=parent
            )
        elif result_row['type'] == 'Season':
            return_obj = Season(
                result_row['path'],
                result_row['show_name'],
                result_row['season_number'],
                parent=parent
            )
        elif result_row['type'] == 'Extra':
            return_obj = Extra(
                result_row['path'],
                result_row['show_name'],
                result_row['season_number'],
                parent=parent
            )
        else:
            print('hmm hmm')
            pass

        if get_children and (
            result_row['containers'] or
            result_row['media']
        ):
            containers, media = self._get_container_children(result_row)

            for c in containers:
                return_obj.containers.append(c)

            for m in media:
                return_obj.media.append(m)

        if result_row['year']:
            return_obj.set_year(result_row['year'])

        if result_row['ext_ids']:
            for ext_id in result_row['ext_ids'].split(","):
                parts = ext_id.split("=")
                return_obj.ext_ids()[parts[0]] = parts[1]

        return return_obj

    def _media_from_data(self, result_row):
        if result_row['parent']:
            parent = self._get_parent(result_row['parent'])
        else:
            parent = None

        if result_row['type'] == 'Movie':
            return_obj = Movie(
                result_row['file_path'],
                result_row['title'],
                parent=parent
            )
        elif result_row['type'] == 'Episode':
            flags = result_row['flags']
            is_oad = flags[0] == "1"
            is_ncop = flags[1] == "1"
            is_nced = flags[2] == "1"
            return_obj = Episode(
                result_row['file_path'],
                result_row['episode_number'],
                parent=parent,
                is_oad=is_oad,
                is_ncop=is_ncop,
                is_nced=is_nced
            )
        else:
            print('hmm hmm')
            pass

        for subtitle in result_row['subtitles'].split(","):
            if subtitle.strip():
                return_obj.subtitles.append(subtitle)

        if result_row['year']:
            return_obj.set_year(result_row['year'])

        if result_row['ext_ids']:
            for ext_id in result_row['ext_ids'].split(","):
                parts = ext_id.split("=")
                return_obj.ext_ids()[parts[0]] = parts[1]

        return return_obj

    def _create_identifiables_table(self):
        self._create_table(
            "identifiables",
            # type: Episode|Movie
            # subtitles: comma separated list
            # title: None for Episode
            # flags: is_oad is_ncop is_nced
            """(
                id TEXT,
                ext_ids TEXT,
                year INTEGER
            )"""
            )

    def _update_identifiables(self, identifiables):

        self._delete_identifiables(identifiables)

        where, ids = self._where_ids(identifiables)

        data = [self._get_identifiable_data(i) for i in identifiables]

        cur = self.conn.cursor()

        sql = """INSERT INTO identifiables (
            id,
            ext_ids,
            year
        ) VALUES (?,?,?)"""

        cur.executemany(sql, data)

        self.conn.commit()

    def _delete_identifiables(self, identifiables):
        if not len(identifiables):
            return

        where, ids = self._where_ids(identifiables)

        cur = self.conn.cursor()

        sql = 'DELETE FROM identifiables WHERE {}'.format(where)
        cur.execute(sql, ids)

        self.conn.commit()

    def _get_identifiable_data(self, identifiable):
        ext_ids = []
        for key in identifiable.ext_ids().keys():
            ext_ids.append(f"{key}={identifiable.ext_ids()[key]}")

        return (
            identifiable.id(),
            ','.join(ext_ids),
            identifiable.year()
        )
