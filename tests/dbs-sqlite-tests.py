import re
import sqlite3
from classes.dbs.sqlite import Sqlite
from classes.container import MediaLibrary, Show, Season, Extra
from classes.media import Episode, Movie

debug = True
debug = False

RANDOM_STR = "foo"
RANDOM_STR2 = "bar"
RANDOM_INT = 22
FAIL = "FAIL"
PASS = "PASS"
TMP_DB = ":memory:"

test_name = "Sqlite.connect"
print(test_name) if debug else ""
try:
    db = Sqlite()

    db.connect(TMP_DB)
    if not isinstance(db.conn, sqlite3.Connection):
        print(test_name, FAIL, 1)

except Exception as e:
    print(test_name, FAIL, 2, e)

finally:
    db.close()

test_name = "Sqlite.close"
print(test_name) if debug else ""
try:
    db = Sqlite()
    db.connect(TMP_DB)

    db.close()

except Exception as e:
    print(test_name, FAIL, 2, e)


def test_table_exist(db, table_name):

    cur = db.conn.cursor()
    cur.execute(
        "SELECT Count() FROM sqlite_master WHERE type='table' and name='{}'"
        .format(table_name)
    )

    return cur.fetchone()[0] > 0


def test_table_pragma(db, table_name, columns):

    cur = db.conn.cursor()
    cols = cur.execute("PRAGMA table_info('{}')".format(table_name)).fetchall()

    errors = 0

    if errors == 0:
        if len(columns) != len(cols):
            errors = 1

    if errors == 0:
        for i in range(len(columns)):
            # columns ('ext_id', 'TEXT')
            # cols (0, 'ext_id', 'TEXT', 0, None, 0)
            if (
                columns[i][0] != cols[i][1] and
                columns[i][1] != cols[i][2]
            ):
                errors = 1
                break

    return errors == 0


def test_table_dublicate(db, table_name):

    cur = db.conn.cursor()
    cur.execute(
        "SELECT Count() FROM sqlite_master WHERE type='table' and name='{}'"
        .format(table_name)
    )

    return cur.fetchone()[0] == 1


def test_data_count(db, table_name, row=[]):
    cur = db.conn.cursor()

    where = ""
    for col in row:
        where = "{}{}='{}' AND ".format(
            where,
            col[0],
            col[1]
        )

    where = where.rstrip("AND ")

    sql = "SELECT Count() FROM {}".format(table_name)
    if where:
        sql = "{} WHERE {}".format(sql, where)

    cur.execute(sql)

    return cur.fetchone()[0]


def parse_cols(col_string):
    temp = col_string.lstrip("(").rstrip(")").split(",")
    cols = []
    for line in temp:
        line = line.strip()
        if line:
            cols.append(tuple(line.split(" ")))

    return tuple(cols)


test_name = "Sqlite.create_title_to_ext_id_table"
print(test_name) if debug else ""
try:
    db = Sqlite()
    db.connect(TMP_DB)
    cur = db.conn.cursor()
    table_name = RANDOM_STR

    db.create_title_to_ext_id_table(table_name)
    if not test_table_exist(db, table_name):
        print(test_name, FAIL, 1)

    SCHEMA = "(ext_id TEXT, title TEXT, year INTEGER, media_type TEXT)"
    cols = parse_cols(SCHEMA)

    if not test_table_pragma(db, table_name, cols):
        print(test_name, FAIL, 2)

    db.create_title_to_ext_id_table(table_name)
    db.create_title_to_ext_id_table(table_name)
    if not test_table_dublicate(db, table_name):
        print(test_name, FAIL, 3)

except Exception as e:
    print(test_name, FAIL, 4, e)

finally:
    db.close()


test_name = "Sqlite.populate_title_to_ext_id_table"
print(test_name) if debug else ""
try:
    db = Sqlite()
    db.connect(TMP_DB)
    cur = db.conn.cursor()
    table_name = RANDOM_STR
    db.create_title_to_ext_id_table(table_name)

    ext_id = RANDOM_STR
    title = RANDOM_STR
    year = RANDOM_INT
    media_type = RANDOM_STR
    test_data = [(ext_id, title, year, media_type)]

    row = (
        ['ext_id', ext_id],
        ['title', title],
        ['year', year],
        ['media_type', media_type]
    )

    db.populate_title_to_ext_id_table(table_name, test_data)
    if not test_data_count(db, table_name, row) > 0:
        print(test_name, FAIL, 1)

    # dublicate
    db.populate_title_to_ext_id_table(table_name, test_data)
    db.populate_title_to_ext_id_table(table_name, test_data)

    if not test_data_count(db, table_name, row) == 1:
        print(test_name, FAIL, 2)

    # delete old
    db.populate_title_to_ext_id_table(table_name, [])
    if not test_data_count(db, table_name, row) == 0:
        print(test_name, FAIL, 3)

except Exception as e:
    print(test_name, FAIL, 4, e)

finally:
    db.close()

test_name = "Sqlite.get_ext_ids"
print(test_name) if debug else ""
try:
    db = Sqlite()
    db.connect(TMP_DB)
    table_name = RANDOM_STR
    db.create_title_to_ext_id_table(table_name)

    ext_id = RANDOM_STR
    title = RANDOM_STR
    year = RANDOM_INT
    media_type = RANDOM_STR
    test_data = [(ext_id, title, year, media_type)]
    db.populate_title_to_ext_id_table(table_name, test_data)

    search_re = re.compile("^{}$".format(title))
    if not db.get_ext_ids(table_name, search_re) == test_data:
        print(test_name, FAIL, 1)

    search_re = re.compile("^.*$")
    if not db.get_ext_ids(table_name, search_re) == test_data:
        print(test_name, FAIL, 2)

    search_re = re.compile("^{}{}$".format(title, RANDOM_STR))
    if not len(db.get_ext_ids(table_name, search_re)) == 0:
        print(test_name, FAIL, 3)

except Exception as e:
    print(test_name, FAIL, 4, e)

finally:
    db.close()


test_name = "Sqlite._create_table"
print(test_name) if debug else ""
try:
    db = Sqlite()
    db.connect(TMP_DB)
    cur = db.conn.cursor()
    table_name = RANDOM_STR

    SCHEMA = "({} TEXT, {} INTEGER)".format(RANDOM_STR, RANDOM_STR2)
    cols = parse_cols(SCHEMA)

    db._create_table(RANDOM_STR, SCHEMA)
    if not test_table_exist(db, table_name):
        print(test_name, FAIL, 1)

    if not test_table_pragma(db, table_name, cols):
        print(test_name, FAIL, 2)

    db._create_table(RANDOM_STR, SCHEMA)
    db._create_table(RANDOM_STR, SCHEMA)
    if not test_table_dublicate(db, table_name):
        print(test_name, FAIL, 3)

except Exception as e:
    print(test_name, FAIL, 4, e)

finally:
    db.close()

test_name = "Sqlite.create_containers_table"
print(test_name) if debug else ""
try:
    db = Sqlite()
    db.connect(TMP_DB)
    cur = db.conn.cursor()
    table_name = "containers"

    cols = parse_cols("""(
        id TEXT,
        type TEXT,
        containers TEXT,
        media TEXT,
        parent TEXT,
        path TEXT,
        show_name TEXT,
        season_number INTEGER
    )""")

    db.create_containers_table()
    if not test_table_pragma(db, table_name, cols):
        print(test_name, FAIL, 1)

except Exception as e:
    print(test_name, FAIL, 2, e)

finally:
    db.close()


test_name = "Sqlite.get_container"
print(test_name) if debug else ""
db = Sqlite()
db.connect(TMP_DB)
db.create_containers_table()

path = "a path"
show_name = "a show name"

media_library = MediaLibrary(path)
show = Show(path, show_name, parent=media_library)
season1 = Season(path, show_name, 1, parent=show)
season2 = Season(path, show_name, 2, parent=show)
season3 = Season(path, show_name, 3, parent=show)
extra = Extra(path, show_name, 1, parent=season1)

media_library.containers.append(show)
show.containers.append(season1)
show.containers.append(season2)
show.containers.append(season3)
season1.containers.append(extra)

db.update_containers([
    media_library,
    show,
    season1,
    season2,
    season3,
    extra
])

result = db.get_container(show)
if (
    result.id() != show.id() or
    not isinstance(result, Show) or
    len(result.containers) != len(show.containers) or
    len(result.media) != len(show.media) or
    result.parent().id() != show.parent().id() or
    result.path() != show.path() or
    result.show_name() != show.show_name()
):
    print(test_name, FAIL, 2)

result2 = db.get_container(show.id())
if result.id() != result2.id():
    print(test_name, FAIL, 2.1)

result = db.get_container(RANDOM_STR)
if result is not None:
    print(test_name, FAIL, 3)

db.close()


test_name = "Sqlite.update_containers"
print(test_name) if debug else ""
db = Sqlite()
db.connect(TMP_DB)
db.create_containers_table()

path = "a path"
show_name = "a show name"

media_library = MediaLibrary(path)
show = Show(path, show_name, parent=media_library)
season1 = Season(path, show_name, 1, parent=show)
season2 = Season(path, show_name, 2, parent=show)
season3 = Season(path, show_name, 3, parent=show)
extra = Extra(path, show_name, 1, parent=season1)

media_library.containers.append(show)
show.containers.append(season1)
show.containers.append(season2)
show.containers.append(season3)
season1.containers.append(extra)

db.update_containers([
    media_library,
    show,
    season1,
    season2,
    season3,
    extra
])
result = db.get_container(show)
if (
    result.id() != show.id() or
    not isinstance(result, Show) or
    len(result.containers) != len(show.containers) or
    len(result.media) != len(show.media) or
    result.parent().id() != show.parent().id() or
    result.path() != show.path() or
    result.show_name() != show.show_name()
):
    print(test_name, FAIL, 2)

if len(result.containers) != 3:
    print(test_name, FAIL, 3)

show.containers.clear()
db.update_containers([show])
result = db.get_container(show)

if (
    result.id() != show.id() or
    not isinstance(result, Show) or
    len(result.containers) != len(show.containers) or
    len(result.media) != len(show.media) or
    result.parent().id() != show.parent().id() or
    result.path() != show.path() or
    result.show_name() != show.show_name()
):
    print(test_name, FAIL, 4)

if len(result.containers) != 0:
    print(test_name, FAIL, 5)

test_data = [media_library, show, season1, season2, season3, extra]
db.update_containers(test_data)
if not test_data_count(db, "containers") == len(test_data):
    print(test_name, FAIL, 6)

# overwrite
db.update_containers(test_data)
if not test_data_count(db, "containers") == len(test_data):
    print(test_name, FAIL, 7)

result = db.get_container(season1)
if (
    result.id() != season1.id() or
    not isinstance(result, Season) or
    len(result.containers) != len(season1.containers) or
    len(result.media) != len(season1.media) or
    result.parent().id() != season1.parent().id() or
    result.path() != season1.path() or
    result.show_name() != season1.show_name() or
    result.season_number() != season1.season_number()
):
    print(test_name, FAIL, 8)

if (
    len(result.containers) != 1 or
    result.season_number() != 1 or
    result.parent().id() != show.id()
):
    print(test_name, FAIL, 9)

db.close()

test_name = "Sqlite.delete_containers"
print(test_name) if debug else ""

db = Sqlite()
db.connect(TMP_DB)
db.create_containers_table()

media_library = MediaLibrary(RANDOM_STR)
show = Show(RANDOM_STR, RANDOM_STR2)

db.update_containers([media_library, show])

if test_data_count(db, "containers") != 2:
    print(test_name, FAIL, 1)

if test_data_count(db, "containers", (['id', media_library.id()],)) != 1:
    print(test_name, FAIL, 2)

db.delete_containers([media_library])

if test_data_count(db, "containers") != 1:
    print(test_name, FAIL, 3)

if test_data_count(db, "containers", (['id', media_library.id()],)) != 0:
    print(test_name, FAIL, 4)
db.close()

test_name = "Sqlite.create_media_table"
print(test_name) if debug else ""

table_name = "media"
cols = parse_cols("""(
    id TEXT,
    type TEXT,
    parent TEXT,
    file_path TEXT,
    subtitles TEXT,
    episode_number INTEGER,
    title TEXT,
    flags TEXT,
    played INTEGER
)""")

db = Sqlite()
db.connect(TMP_DB)
cur = db.conn.cursor()

db.create_media_table()
if not test_table_pragma(db, table_name, cols):
    print(test_name, FAIL)

db.close()

test_name = "Sqlite.update_media"
print(test_name) if debug else ""
db = Sqlite()
db.connect(TMP_DB)
db.create_containers_table()
db.create_media_table()

lib_path = "a path"
file_path = "a file path"
file_path2 = "another file path"
show_name = "a show name"
subtitle_path = "a subtitle path"
title = "a title"

media_library = MediaLibrary(path)
show = Show(lib_path, show_name, parent=media_library)
season1 = Season(lib_path, show_name, 1, parent=show)
season2 = Season(lib_path, show_name, 2 + 1, parent=show)
season3 = Season(lib_path, show_name, 3, parent=show)
extra = Extra(lib_path, show_name, 1, parent=season1)
episode1 = Episode(file_path, 1, False, parent=season1)
episode1.subtitles.append(subtitle_path)
movie = Movie(file_path2, title, False, parent=media_library)

media_library.containers.append(show)
media_library.media.append(movie)
show.containers.append(season1)
show.containers.append(season2)
show.containers.append(season3)
season1.containers.append(extra)
season1.media.append(episode1)

db.update_containers([
    media_library,
    show,
    season1,
    season2,
    season3,
    extra
])

db.update_media([episode1, movie])
result = db.get_media(episode1)
if (
    result.id() != episode1.id() or
    not isinstance(result, Episode) or
    result.parent().id() != episode1.parent().id() or
    result.file_path() != episode1.file_path() or
    len(result.subtitles) != len(episode1.subtitles) or
    result.episode_number() != episode1.episode_number() or
    result.is_oad() != episode1.is_oad() or
    result.is_ncop() != episode1.is_ncop() or
    result.is_nced() != episode1.is_nced() or
    result.played() != episode1.played()
):
    print(test_name, FAIL, 2)

result2 = db.get_media(episode1.id())
if result.id() != result2.id():
    print(test_name, FAIL, 2.1)

result2 = db.get_media(RANDOM_STR)
if result2 is not None:
    print(test_name, FAIL, 2.2)

if len(result.subtitles) != 1:
    print(test_name, FAIL, 3)

episode1.subtitles.clear()
db.update_media([episode1])
result = db.get_media(episode1)
if (
    result.id() != episode1.id() or
    not isinstance(result, Episode) or
    result.parent().id() != episode1.parent().id() or
    result.file_path() != episode1.file_path() or
    len(result.subtitles) != len(episode1.subtitles) or
    result.episode_number() != episode1.episode_number() or
    result.is_oad() != episode1.is_oad() or
    result.is_ncop() != episode1.is_ncop() or
    result.is_nced() != episode1.is_nced() or
    result.played() != episode1.played()
):
    print(test_name, FAIL, 4)

if len(result.subtitles) != 0:
    print(test_name, FAIL, 5)

test_data = [movie, episode1]
db.update_media(test_data)
if not test_data_count(db, "media") == len(test_data):
    print(test_name, FAIL, 6)

# overwrite
db.update_media(test_data)
if not test_data_count(db, "media") == len(test_data):
    print(test_name, FAIL, 7)

result = db.get_media(episode1)
if (
    result.id() != episode1.id() or
    not isinstance(result, Episode) or
    result.parent().id() != episode1.parent().id() or
    result.file_path() != episode1.file_path() or
    len(result.subtitles) != len(episode1.subtitles) or
    result.episode_number() != episode1.episode_number() or
    result.is_oad() != episode1.is_oad() or
    result.is_ncop() != episode1.is_ncop() or
    result.is_nced() != episode1.is_nced() or
    result.played() != episode1.played()
):
    print(test_name, FAIL, 8)

result = db.get_media(movie)
if (
    result.id() != movie.id() or
    not isinstance(result, Movie) or
    result.parent().id() != movie.parent().id() or
    result.file_path() != movie.file_path() or
    len(result.subtitles) != len(movie.subtitles) or
    result.title() != movie.title()
):
    print(test_name, FAIL, 9)

episode3 = Episode(
    "3{}".format(file_path), 3, False, parent=season1, is_ncop=True
)
episode2 = Episode(
    "2{}".format(file_path), 2, False, parent=season1, is_oad=True
)
episode4 = Episode(
    "4{}".format(file_path), 4, False, parent=season1, is_nced=True
)
season1.containers.append(episode2)
season1.containers.append(episode3)
season1.containers.append(episode4)
db.update_containers([season1])
db.update_media([episode2, episode3, episode4])

result = db.get_media(episode2)
if not result.is_oad() or result.is_ncop() or result.is_nced():
    print(test_name, FAIL, 10)

result = db.get_media(episode3)
if result.is_oad() or not result.is_ncop() or result.is_nced():
    print(test_name, FAIL, 11)

result = db.get_media(episode4)
if result.is_oad() or result.is_ncop() or not result.is_nced():
    print(test_name, FAIL, 12)

movie = Movie(file_path2, title, False, parent=media_library)
episode5 = Episode("5{}".format(file_path), 5, False, parent=season1)
db.update_media([movie, episode5])
result1 = db.get_media(movie)
result2 = db.get_media(episode5)
if (
    movie.played() !=
    episode5.played() !=
    result1.played() !=
    result2.played() is not
    False
):
    print(test_name, FAIL, 13)

movie.set_played(True)
episode5.set_played(True)
db.update_media([movie, episode5])
result1 = db.get_media(movie)
result2 = db.get_media(episode5)
if (
    movie.played() !=
    episode5.played() !=
    result1.played() !=
    result2.played() is not
    True
):
    print(test_name, FAIL, 13)


db.close()

test_name = "Sqlite.delete_media"
print(test_name) if debug else ""

db = Sqlite()
db.connect(TMP_DB)
db.create_media_table()

movie = Movie("a file_path", "a title", False)
movie2 = Movie("another file_path", "another title", False)

if test_data_count(db, "media") != 0:
    print(test_name, FAIL, 1)

db.update_media([movie, movie2])

if test_data_count(db, "media") != 2:
    print(test_name, FAIL, 2)

if test_data_count(db, "media", (['id', movie.id()],)) != 1:
    print(test_name, FAIL, 3)

db.delete_media([movie])

if test_data_count(db, "media") != 1:
    print(test_name, FAIL, 3)

if test_data_count(db, "media", (['id', movie.id()],)) != 0:
    print(test_name, FAIL, 4)
db.close()

test_name = "Sqlite.create_identifiable_table"
print(test_name) if debug else ""

db = Sqlite()
db.connect(TMP_DB)
cur = db.conn.cursor()
table_name = "identifiables"

cols = parse_cols(
    """(
        item_id TEXT,
        ext_ids TEXT,
        year INTEGER
    )"""
)

db.create_media_table()
if not test_table_pragma(db, table_name, cols):
    print(test_name, FAIL, 1)

db.close()

db.connect(TMP_DB)
cur = db.conn.cursor()
db.create_containers_table()
if not test_table_pragma(db, table_name, cols):
    print(test_name, FAIL, 2)

db.close()

test_name = "Sqlite.update_identifiables"
print(test_name) if debug else ""
db = Sqlite()
db.connect(TMP_DB)
db.create_containers_table()
db.create_media_table()

lib_path = "a path"
file_path = "a file path"
file_path2 = "another file path"
show_name = "a show name"
subtitle_path = "a subtitle path"
title = "a title"

media_library = MediaLibrary(path)
show = Show(lib_path, show_name, parent=media_library)
season1 = Season(lib_path, show_name, 1, parent=show)
season2 = Season(lib_path, show_name, 2 + 1, parent=show)
season3 = Season(lib_path, show_name, 3, parent=show)
extra = Extra(lib_path, show_name, 1, parent=season1)
episode1 = Episode(file_path, 1, False, parent=season1)
episode1.subtitles.append(subtitle_path)
movie = Movie(file_path2, title, False, parent=media_library)

media_library.containers.append(show)
media_library.media.append(movie)
show.containers.append(season1)
show.containers.append(season2)
show.containers.append(season3)
season1.containers.append(extra)
season1.media.append(episode1)

db.update_containers([
    media_library,
    show,
    season1,
    season2,
    season3,
    extra
])

db.update_media([episode1, movie])

if (
    (movie.year() != show.year()) is not None and
    (len(movie.ext_ids()) != len(show.ext_ids())) != 0
):
    print(test_name, FAIL, 1)

MOVIE_YEAR = 2000
movie.set_year(MOVIE_YEAR)
db.update_media([movie])
result = db.get_media(movie)
if result.year() != MOVIE_YEAR:
    print(test_name, FAIL, 2)

SHOW_YEAR = 2001
show.set_year(SHOW_YEAR)
db.update_containers([show])
result = db.get_container(show)
if result.year() != SHOW_YEAR:
    print(test_name, FAIL, 3)

movie.ext_ids()[RANDOM_STR] = RANDOM_STR2
movie.ext_ids()[RANDOM_STR2] = RANDOM_STR
db.update_media([movie])
result = db.get_media(movie)
if (
    len(result.ext_ids()) != 2 and
    result.ext_ids()[RANDOM_STR] != RANDOM_STR2 and
    result.ext_ids()[RANDOM_STR2] != RANDOM_STR
):
    print(test_name, FAIL, 2)

show.ext_ids()[RANDOM_STR] = RANDOM_STR2
show.ext_ids()[RANDOM_STR2] = RANDOM_STR
db.update_containers([show])
result = db.get_container(show)
if (
    len(result.ext_ids()) != 2 and
    result.ext_ids()[RANDOM_STR] != RANDOM_STR2 and
    result.ext_ids()[RANDOM_STR2] != RANDOM_STR
):
    print(test_name, FAIL, 2)

db.close()

print("db-sqlite-tests: Successfully Completed")
