import re
import sqlite3
import unittest
from classes.dbs.sqlite import Sqlite
from classes.container import Container, MediaLibrary, Show, Season, Extra
from classes.identifiable import Identifiable
from classes.media import Episode, Movie
from classes.meta import Meta, Episode_Meta
import test.testutils as testutils

debug = True
debug = False

RANDOM_STR = "foo"
RANDOM_STR2 = "bar"
RANDOM_INT = 22
FAIL = "FAIL"
PASS = "PASS"
TMP_DB = ":memory:"


def create_test_library():
    meta = create_test_meta()

    media_lib = MediaLibrary("apath", parent=None)

    show1 = Show(media_lib.path(), "Show 1", parent=media_lib)
    show1.ext_ids()['TestID'] = '1'
    show1.set_meta(meta[0])
    media_lib.containers.append(show1)

    show2 = Show(media_lib.path(), "Show 2", parent=media_lib)
    show2.ext_ids()['TestID'] = '2'
    show2.set_meta(meta[1])
    media_lib.containers.append(show2)

    movie = Movie("moviepath", "atitle", False, parent=media_lib)
    movie.ext_ids()['TestID'] = '3'
    movie.set_meta(meta[2])
    media_lib.media.append(movie)

    season1 = Season(show1.path(), show1.show_name(), 1, parent=show1)
    show1.containers.append(season1)

    season2 = Season(show1.path(), show1.show_name(), 2, parent=show1)
    show1.containers.append(season2)

    extra1 = Extra(
        season1.path(), season1.show_name(), season1.season_number(),
        parent=season1
    )
    season1.containers.append(extra1)

    extra2 = Extra(
        show2.path(), show2.show_name(), 0, parent=show2
    )
    show2.containers.append(extra2)

    episode1 = Episode(
        "episode1path", 1, False, parent=season1, is_oad=False,
        is_ncop=False, is_nced=False, is_ova=False
    )
    season1.media.append(episode1)

    episode2 = Episode(
        "episode2path", 2, False, parent=season1, is_oad=False,
        is_ncop=False, is_nced=False, is_ova=False
    )
    season1.media.append(episode2)

    episode3 = Episode(
        "episode3path", 3, False, parent=extra1, is_oad=False,
        is_ncop=False, is_nced=False, is_ova=False
    )
    extra1.media.append(episode3)

    episode4 = Episode(
        "episode4path", 4, False, parent=extra2, is_oad=False,
        is_ncop=False, is_nced=False, is_ova=False
    )
    extra2.media.append(episode4)

    episode5 = Episode(
        "episode5path", 5, False, parent=show2, is_oad=False,
        is_ncop=False, is_nced=False, is_ova=False
    )
    show2.media.append(episode5)

    root = media_lib
    containers = [media_lib, show1, show2, season1, season2, extra1, extra2]
    media = [movie, episode1, episode2, episode3, episode4, episode5]

    return root, containers, media


def create_test_meta():

    show1_meta = Meta(
        'TestID:::1',
        'meta show1 title',
        2.1,
        'show1_poster',
        [],
        'meta show1 description'
    )

    show2_meta = Meta(
        'TestID:::2',
        'meta show2 title',
        3.1,
        'show2_poster',
        [
            Episode_Meta(
                5,
                "meta episode5 title",
                "meta episode5 summary"
            )
        ],
        'meta show1 description'
    )

    movie_meta = Meta(
        'TestID:::3',
        'meta movie title',
        1.1,
        'movie_poster',
        [],
        'movie meta description')

    return [show1_meta, show2_meta, movie_meta]


def table_count(db, table_name, table_schema=""):
    cur = db.conn.cursor()
    sql = '''
        select count() from sqlite_master
        where type='table'
        and name = ?
        and sql LIKE '%' || ?
        '''

    cur.execute(sql, (table_name, table_schema))
    return cur.fetchone()[0]


def remove_double_spaces(str):
    return re.sub(r'\s+', " ", str)


class TestSqlite(unittest.TestCase):

    def test_connect(self):
        db = Sqlite()
        self.assertIsNone(db.conn)

        db.connect(database=TMP_DB)
        self.assertIsInstance(db.conn, sqlite3.Connection)

        db.close()

    def test_close(self):
        db = Sqlite()
        db.connect(database=TMP_DB)
        db.close()
        with self.assertRaisesRegex(
            sqlite3.ProgrammingError,
            r'Cannot operate on a closed database.'
        ):
            db.conn.cursor()
        db.close()

    def test__create_table(self):
        db = Sqlite()
        db.connect(database=TMP_DB)

        table_name = "randomtable"
        table_schema = remove_double_spaces(
            """(
                media_id TEXT,
                played INTEGER
            )"""
        )

        db._create_table(table_name, table_schema)

        count = table_count(db, table_name, table_schema)
        self.assertEqual(count, 1)

        # create if not EXISTS
        db._create_table(table_name, table_schema)

        count = table_count(db, table_name, table_schema)
        self.assertEqual(count, 1)

        db.close()

    def test__create_title_to_ext_id_table(self):
        db = Sqlite()
        db.connect(database=TMP_DB)

        table_name = "randomtable"
        table_schema = remove_double_spaces(
            "(ext_id TEXT, title TEXT, year INTEGER, media_type TEXT)"
        )

        db._create_title_to_ext_id_table(table_name)

        count = table_count(db, table_name, table_schema)

        db.close()

        self.assertEqual(count, 1)

    def test_create_containers_table(self):
        db = Sqlite()
        db.connect(database=TMP_DB)

        table_name = "containers"
        identifiables_table_name = "identifiables"
        meta_table_name = "meta"
        table_schema = remove_double_spaces(
            """(
                id TEXT,
                type TEXT,
                containers TEXT,
                media TEXT,
                parent_id TEXT,
                path TEXT,
                show_name TEXT,
                season_number INTEGER
            )"""
        )

        db.create_containers_table()

        count = table_count(db, table_name, table_schema)
        identifiables_count = table_count(db, identifiables_table_name)
        meta_count = table_count(db, meta_table_name)

        db.close()

        self.assertEqual(count, 1)
        self.assertEqual(identifiables_count, 1)
        self.assertEqual(meta_count, 1)

    def test_create_media_table(self):
        db = Sqlite()
        db.connect(database=TMP_DB)

        table_name = "media"
        identifiables_table_name = "identifiables"
        media_states_table_name = "media_states"
        table_schema = remove_double_spaces(
            """(
                id TEXT,
                type TEXT,
                parent_id TEXT,
                file_path TEXT,
                subtitles TEXT,
                episode_number INTEGER,
                title TEXT,
                flags TEXT
            )"""
        )

        db.create_media_table()

        count = table_count(db, table_name, table_schema)
        identifiables_count = table_count(db, identifiables_table_name)
        media_states_count = table_count(db, media_states_table_name)

        db.close()

        self.assertEqual(count, 1)
        self.assertEqual(identifiables_count, 1)
        self.assertEqual(media_states_count, 1)

    def test_create_watchlist_table(self):
        db = Sqlite()
        db.connect(database=TMP_DB)

        table_name = "watchlist"
        table_schema = remove_double_spaces(
            "(show_id TEXT)"
        )

        db.create_watchlist_table()

        count = table_count(db, table_name, table_schema)

        db.close()

        self.assertEqual(count, 1)

    def test_create_meta_table(self):
        db = Sqlite()
        db.connect(database=TMP_DB)

        table_name = "meta"
        table_schema = remove_double_spaces(
            """(
                meta_id TEXT,
                meta_title TEXT,
                meta_rating REAL,
                meta_image_name TEXT,
                meta_episodes TEXT,
                meta_description TEXT
            )"""
        )

        db._create_meta_table()

        count = table_count(db, table_name, table_schema)

        db.close()

        self.assertEqual(count, 1)

    def test__create_identifiables_table(self):
        db = Sqlite()
        db.connect(database=TMP_DB)

        table_name = "identifiables"
        table_schema = remove_double_spaces(
            """(
                id TEXT,
                ext_ids TEXT,
                year INTEGER
            )"""
        )

        db._create_identifiables_table()

        count = table_count(db, table_name, table_schema)

        db.close()

        self.assertEqual(count, 1)

    def test__create_media_states_table(self):
        db = Sqlite()
        db.connect(database=TMP_DB)

        table_name = "media_states"
        table_schema = remove_double_spaces(
            """(
                media_id TEXT,
                played INTEGER
            )"""
        )

        db._create_media_states_table()

        count = table_count(db, table_name, table_schema)

        db.close()

        self.assertEqual(count, 1)

    def test_populate_title_to_ext_id_table(self):
        db = Sqlite()
        db.connect(database=TMP_DB)

        table_name = "randomtable"
        test_data = [
            ('ext_id', 'title', 2000, 'media_type'),
            ('ext_id2', 'title2', 2001, 'media_type2')
        ]

        db.populate_title_to_ext_id_table(table_name, test_data)

        sql = f'select count() from {table_name} where ext_id=?'
        cur = db.conn.cursor()

        cur.execute(sql, (test_data[0][0],))
        count = cur.fetchone()[0]

        self.assertEqual(count, 1)

        # remove old data
        db.populate_title_to_ext_id_table(table_name, test_data)

        cur.execute(sql, (test_data[0][0],))
        count = cur.fetchone()[0]

        self.assertEqual(count, 1)

        # remove old data
        db.populate_title_to_ext_id_table(table_name, [])

        cur.execute(sql, (test_data[0][0],))
        count = cur.fetchone()[0]

        self.assertEqual(count, 0)

        db.close()

    def test_update_and_get_containers(self):
        root, containers, media = create_test_library()

        db = Sqlite()
        db.connect(database=TMP_DB)

        db.create_containers_table()
        db.create_media_table()
        db.update_media(media)
        db.update_meta(create_test_meta())

        db.update_containers(containers)

        sql = f'select count() from containers'
        cur = db.conn.cursor()
        cur.execute(sql)
        count = cur.fetchone()[0]

        self.assertEqual(count, len(containers))

        for con in containers:
            db_container = db.get_container(con.id())
            self.assertTrue(testutils.compare_containers(con, db_container))

        # dublicates
        con = containers[0]
        db.update_containers([con])

        sql = f'select count() from containers where id=?'
        cur = db.conn.cursor()
        cur.execute(sql, (con.id(),))
        count = cur.fetchone()[0]

        self.assertEqual(count, 1)

        a_season = None
        for con in containers:
            if isinstance(con, Season):
                a_season = con
                break

        if a_season:
            a_season._path = a_season.path() + "foo"
            a_season._show_name = a_season.show_name() + "foo"
            a_season._season_number = a_season.season_number() + 1
            a_season._parent = None

            if (len(a_season.containers)):
                a_season.containers.clear()
            else:
                for c in containers:
                    if isinstance(c, Extra):
                        a_season.containers.append(c)
                        c.set_parent(a_season)
                        break
            if (len(a_season.media)):
                a_season.media.clear()
            else:
                for m in media:
                    if isinstance(m, Episode):
                        a_season.media.append(m)
                        m.set_parent(a_season)
                        break

            db.update_containers([a_season])
            db_container = db.get_container(a_season.id())
            self.assertTrue(testutils.compare_containers(
                a_season,
                db_container
            ))

        db.close()

    def test_update_and_get_media(self):
        root, containers, media = create_test_library()

        db = Sqlite()
        db.connect(database=TMP_DB)

        db.create_containers_table()
        db.create_media_table()
        db.update_containers(containers)
        db.update_meta(create_test_meta())

        db.update_media(media)

        sql = f'select count() from media'
        cur = db.conn.cursor()
        cur.execute(sql)
        count = cur.fetchone()[0]

        self.assertEqual(count, len(media))

        for med in media:
            db_media = db.get_media(med.id())
            self.assertTrue(testutils.compare_media(med, db_media))

        # dublicates
        med = media[0]
        db.update_media([med])

        sql = f'select count() from media where id=?'
        cur = db.conn.cursor()
        cur.execute(sql, (med.id(),))
        count = cur.fetchone()[0]

        self.assertEqual(count, 1)

        a_movie = None
        for med in media:
            if isinstance(med, Movie):
                a_movie = med
                break

        if a_movie:
            a_movie._file_path = a_movie.file_path() + "foo"
            a_movie._title = a_movie.title() + "foo"
            a_movie._played = not a_movie._played
            a_movie._parent = None

            db.update_media([a_movie])
            db_movie = db.get_media(a_movie.id())
            self.assertTrue(testutils.compare_media(a_movie, db_movie))

        an_episode = None
        for med in media:
            if isinstance(med, Episode):
                an_episode = med
                break

        if an_episode:
            an_episode._file_path = an_episode.file_path() + "foo"
            an_episode._episode_number = an_episode.episode_number() + 1
            an_episode._played = not an_episode._played
            an_episode._parent = None
            an_episode._is_oad = not an_episode.is_oad()
            an_episode._is_ncop = not an_episode.is_ncop()
            an_episode._is_nced = not an_episode.is_nced()
            an_episode._is_ova = not an_episode.is_ova()

            db.update_media([an_episode])
            db_episode = db.get_media(an_episode.id())
            self.assertTrue(testutils.compare_media(an_episode, db_episode))

        db.close()

    def test_update_meta(self):
        meta = create_test_meta()

        db = Sqlite()
        db.connect(database=TMP_DB)

        db.update_meta(meta)

        sql = f'select count() from meta'
        cur = db.conn.cursor()
        cur.execute(sql)
        count = cur.fetchone()[0]

        self.assertEqual(count, len(meta))

        # dublicates
        db.update_meta(meta)
        db.update_meta(meta)

        cur.execute(sql)
        count = cur.fetchone()[0]

        self.assertEqual(count, len(meta))

        db.close()

    def test__update_identifiables(self):
        root, containers, media = create_test_library()
        identifiables = [
            i for i in (containers + media) if isinstance(i, Identifiable)
        ]

        db = Sqlite()
        db.connect(database=TMP_DB)

        db.create_containers_table()
        db.update_containers(containers)
        db.create_media_table()
        db.update_media(media)
        db.update_meta(create_test_meta())

        sql = f'select count() from identifiables'
        cur = db.conn.cursor()
        cur.execute(sql)
        count = cur.fetchone()[0]

        self.assertEqual(count, len(identifiables))

        for ide in identifiables:
            if isinstance(ide, Container):
                db_identifiable = db.get_container(ide.id())
            else:
                db_identifiable = db.get_media(ide.id())

            self.assertTrue(testutils.compare_identifiables(
                ide,
                db_identifiable
            ))

        # dublicates
        ide = identifiables[0]
        db._update_identifiables([ide])

        sql = f'select count() from identifiables where id=?'
        cur = db.conn.cursor()
        cur.execute(sql, (ide.id(),))
        count = cur.fetchone()[0]

        self.assertEqual(count, 1)

        an_identifiable = identifiables[0]

        if an_identifiable:
            year = an_identifiable.year() + 1 if an_identifiable.year() else 1
            an_identifiable.set_year(year)
            an_identifiable.ext_ids()["foo"] = "bar"

            if isinstance(an_identifiable, Container):
                db.update_containers([an_identifiable])
                db_identifiable = db.get_container(an_identifiable.id())
            else:
                db.update_media([an_identifiable])
                db_identifiable = db.get_media(an_identifiable.id())

            self.assertTrue(testutils.compare_identifiables(
                an_identifiable,
                db_identifiable
            ))

        db.close()

    def test__update_media_states(self):
        root, containers, media = create_test_library()
        meta = create_test_meta()

        db = Sqlite()
        db.connect(database=TMP_DB)

        db.create_containers_table()
        db.create_media_table()
        db.update_containers(containers)
        db.update_media(media)

        sql = f'select count() from media_states'
        cur = db.conn.cursor()
        cur.execute(sql)
        count = cur.fetchone()[0]

        self.assertEqual(count, len(media))

        for med in media:
            db_media = db.get_media(med.id())
            self.assertTrue(testutils.compare_media_states(med, db_media))

        # dublicates
        a_media = media[0]
        db.update_media([a_media])

        sql = f'select count() from media_states where media_id=?'
        cur = db.conn.cursor()
        cur.execute(sql, (a_media.id(),))
        count = cur.fetchone()[0]

        self.assertEqual(count, 1)

        a_media = media[0]

        if a_media:
            a_media.set_played(not a_media.played())

            db.update_media([a_media])
            db_media = db.get_media(a_media.id())
            self.assertTrue(testutils.compare_media_states(a_media, db_media))

            a_media.set_played(not a_media.played())
            db.update_media([a_media], overwrite_media_states=False)
            db_media = db.get_media(a_media.id())
            self.assertFalse(testutils.compare_media_states(a_media, db_media))

        db.close()

    def test_delete_containers(self):
        root, containers, media = create_test_library()

        db = Sqlite()
        db.connect(database=TMP_DB)

        db.create_containers_table()
        db.create_media_table()
        db.update_media(media)
        db.update_containers(containers)

        con = containers[0]
        db.delete_containers([con])

        sql = f'select count() from containers'
        cur = db.conn.cursor()
        cur.execute(sql)
        count = cur.fetchone()[0]

        self.assertEqual(count, len(containers) - 1)

        db.delete_containers(containers)

        sql = f'select count() from containers'
        cur = db.conn.cursor()
        cur.execute(sql)
        count = cur.fetchone()[0]

        self.assertEqual(count, 0)

        db.close()

    def test_delete_media(self):
        root, containers, media = create_test_library()

        db = Sqlite()
        db.connect(database=TMP_DB)

        db.create_containers_table()
        db.create_media_table()
        db.update_media(media)
        db.update_containers(containers)

        med = media[0]
        db.delete_media([med])

        sql = f'select count() from media'
        cur = db.conn.cursor()
        cur.execute(sql)
        count = cur.fetchone()[0]

        self.assertEqual(count, len(media) - 1)

        db.delete_media(media)

        sql = f'select count() from media'
        cur = db.conn.cursor()
        cur.execute(sql)
        count = cur.fetchone()[0]

        self.assertEqual(count, 0)

        db.close()

    def test__delete_identifiables(self):
        root, containers, media = create_test_library()
        identifiables = [
            i for i in (containers + media) if isinstance(i, Identifiable)
        ]

        db = Sqlite()
        db.connect(database=TMP_DB)

        db.create_containers_table()
        db.update_containers(containers)
        db.create_media_table()
        db.update_media(media)

        ide = identifiables[0]
        db._delete_identifiables([ide])

        sql = f'select count() from identifiables'
        cur = db.conn.cursor()
        cur.execute(sql)
        count = cur.fetchone()[0]

        self.assertEqual(count, len(identifiables) - 1)

        db._delete_identifiables(identifiables)

        sql = f'select count() from identifiables'
        cur = db.conn.cursor()
        cur.execute(sql)
        count = cur.fetchone()[0]

        self.assertEqual(count, 0)

        db.close()

    def test__delete_media_states(self):
        root, containers, media = create_test_library()

        db = Sqlite()
        db.connect(database=TMP_DB)

        db.create_containers_table()
        db.create_media_table()
        db.update_media(media)
        db.update_containers(containers)

        med = media[0]
        db._delete_media_states([(med.id(), med.played())])

        sql = f'select count() from media_states'
        cur = db.conn.cursor()
        cur.execute(sql)
        count = cur.fetchone()[0]

        self.assertEqual(count, len(media) - 1)

        db._delete_media_states([(m.id(), m.played()) for m in media])

        sql = f'select count() from media_states'
        cur = db.conn.cursor()
        cur.execute(sql)
        count = cur.fetchone()[0]

        self.assertEqual(count, 0)

        db.close()

    def test__delete_meta(self):
        meta = create_test_meta()

        db = Sqlite()
        db.connect(database=TMP_DB)

        db.update_meta(meta)

        met = meta[0]
        db._delete_meta([met])

        sql = f'select count() from meta'
        cur = db.conn.cursor()
        cur.execute(sql)
        count = cur.fetchone()[0]

        self.assertEqual(count, len(meta) - 1)

        db._delete_meta(meta)

        sql = f'select count() from meta'
        cur = db.conn.cursor()
        cur.execute(sql)
        count = cur.fetchone()[0]

        self.assertEqual(count, 0)

        db.close()

    def test__get_container_data(self):
        root, containers, media = create_test_library()

        for item in containers:
            item_data = Sqlite()._get_container_data(item)

            self.assertEqual(item.id(), item_data[0])
            self.assertEqual(item.__class__.__name__, item_data[1])
            self.assertEqual(
                ','.join([c.id() for c in item.containers]),
                item_data[2]
            )
            self.assertEqual(
                ','.join([m.id() for m in item.media]),
                item_data[3]
            )
            self.assertEqual(
                item.parent().id() if item.parent() else None,
                item_data[4]
            )
            self.assertEqual(item.path(), item_data[5])
            self.assertEqual(
                item.show_name() if hasattr(item, 'show_name') else None,
                item_data[6]
            )
            self.assertEqual(
                (
                    item.season_number()
                    if hasattr(item, 'season_number') and item.season_number()
                    else 0
                ),
                item_data[7]
            )

    def test__get_media_data(self):
        root, containers, media = create_test_library()

        for item in media:
            if isinstance(item, Episode):
                flags = "{}{}{}{}".format(
                    1 if item.is_oad() else 0,
                    1 if item.is_ncop() else 0,
                    1 if item.is_nced() else 0,
                    1 if item.is_ova() else 0
                )
            else:
                flags = None

            item_data = Sqlite()._get_media_data(item)

            self.assertEqual(item.id(), item_data[0])
            self.assertEqual(item.__class__.__name__, item_data[1])
            self.assertEqual(
                item.parent().id() if item.parent() else None,
                item_data[2]
            )
            self.assertEqual(item.file_path(), item_data[3])
            self.assertEqual(','.join(item.subtitles), item_data[4])
            self.assertEqual(
                (
                    item.episode_number()
                    if isinstance(item, Episode)
                    else None
                ),
                item_data[5]
            )
            self.assertEqual(
                item.title() if isinstance(item, Movie) else None,
                item_data[6]
            )
            self.assertEqual(flags, item_data[7])

    def test__get_identifiable_data(self):
        root, containers, media = create_test_library()
        identifiables = [
            i for i in containers + media if isinstance(i, Identifiable)
        ]

        for item in identifiables:
            ext_ids = []
            for key in item.ext_ids().keys():
                ext_ids.append(f"{key}:::{item.ext_ids()[key]}---")

            item_data = Sqlite()._get_identifiable_data(item)

            self.assertEqual(item.id(), item_data[0])
            self.assertEqual(';;;'.join(ext_ids), item_data[1])
            self.assertEqual(item.year(), item_data[2])

    def test__get_media_states_data(self):
        root, containers, media = create_test_library()

        self.assertTrue(
            [(m.id(), m.played()) for m in media] ==
            Sqlite()._get_media_states_data(media)
        )

    def test__get_meta_data(self):
        meta = create_test_meta()

        self.assertTrue([
            (
                m.id(),
                m.title(),
                m.rating(),
                m.image_name(),
                ';;;'.join(
                    [':::'.join([
                        str(e.episode_number()),
                        e.title(),
                        e.summary()
                    ]) for e in m.episodes()]
                ),
                m.description(),
            ) for m in meta] == Sqlite()._get_meta_data(meta)
        )

    def test_get_unplayed_count(self):
        root, containers, media = create_test_library()

        db = Sqlite()
        db.connect(database=TMP_DB)

        db.create_containers_table()
        db.create_media_table()
        db.update_media(media)
        db.update_containers(containers)

        self.assertEqual(
            db.get_unplayed_count(root.id()),
            len(media)
        )

        media[0].set_played(True)
        db.update_media([media[0]])

        self.assertEqual(
            db.get_unplayed_count(root.id()),
            len(media) - 1
        )

        media[0].set_played(False)
        db.update_media([media[0]])

        self.assertEqual(
            db.get_unplayed_count(root.id()),
            len(media)
        )

        db.close()

    def test_set_played(self):
        root, containers, media = create_test_library()

        db = Sqlite()
        db.connect(database=TMP_DB)

        db.create_containers_table()
        db.create_media_table()
        db.update_media(media)
        db.update_containers(containers)

        self.assertEqual(db.get_unplayed_count(root.id()), len(media))

        db.set_played(root.id(), True)

        self.assertEqual(db.get_unplayed_count(root.id()), 0)

        db.set_played(root.id(), False)

        self.assertEqual(db.get_unplayed_count(root.id()), len(media))

        db.close()

        db.connect()

        con = '34ba81959a86317eb75206ffdab76512'
        print(db.get_unplayed_count(con))
        db.set_played(con, True)
        print(db.get_unplayed_count(con))


    def test_watchlist(self):
        root, containers, media = create_test_library()

        db = Sqlite()
        db.connect(database=TMP_DB)

        db.create_containers_table()
        db.create_media_table()
        db.update_media(media)
        db.update_containers(containers)
        db.create_watchlist_table()

        container = containers[0]
        CONTAINER_ID = container.id()

        self.assertFalse(db.is_in_watchlists(CONTAINER_ID))

        db.add_to_watchlist([CONTAINER_ID])
        self.assertTrue(db.is_in_watchlists(CONTAINER_ID))

        list = db.get_watchlist()
        self.assertEqual(len(list), 1)
        self.assertTrue(testutils.compare_containers(list[0], container))

        db.remove_from_watchlist([CONTAINER_ID])
        self.assertFalse(db.is_in_watchlists(CONTAINER_ID))

        db.add_to_watchlist([
            containers[0].id(),
            containers[1].id()
        ])
        self.assertEqual(len(db.get_watchlist()), 2)
        db.remove_all_from_watchlist()
        self.assertEqual(len(db.get_watchlist()), 0)

        db.add_to_watchlist([CONTAINER_ID])
        self.assertTrue(db.is_in_watchlists(CONTAINER_ID))
        db.delete_containers([container])
        self.assertIsNone(db.get_container(CONTAINER_ID))
        list = db.get_watchlist()
        self.assertEqual(len(list), 0)
        self.assertFalse(db.is_in_watchlists(CONTAINER_ID))

        db.close()

    def test_get_ext_ids(self):
        root, containers, media = create_test_library()

        db = Sqlite()
        db.connect(database=TMP_DB)

        TABLE_NAME = "randomtable"
        TITLE = "foo"
        TEST_DATA = [
            ('ext_id', TITLE, 2000, 'media_type'),
            ('ext_id2', TITLE + "bar", 2001, 'media_type2')
        ]

        db.populate_title_to_ext_id_table(TABLE_NAME, TEST_DATA)

        self.assertEqual(
            db.get_ext_ids(TABLE_NAME, re.compile("^.*$")),
            TEST_DATA
        )

        self.assertEqual(
            db.get_ext_ids(TABLE_NAME, re.compile(TITLE)),
            TEST_DATA
        )

        self.assertEqual(
            db.get_ext_ids(TABLE_NAME, re.compile(f"^{TITLE}$")),
            [TEST_DATA[0]]
        )

        db.close()


if __name__ == '__main__':
    unittest.main()
