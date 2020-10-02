import re
import sqlite3
from classes.dbs.sqlite import Sqlite
from classes.container import MediaLibrary, Show, Season, Extra

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
season2 = Season(path, show_name, 2 + 1, parent=show)
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
season2 = Season(path, show_name, 2 + 1, parent=show)
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

print("db-sqlite-tests: Successfully Completed")
