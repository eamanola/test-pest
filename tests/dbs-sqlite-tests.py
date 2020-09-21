import re
import sqlite3
from classes.dbs.sqlite import Sqlite

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

test_name = "Sqlite.create_title_to_ext_id_table"
print(test_name) if debug else ""
try:
    db = Sqlite()
    db.connect(TMP_DB)
    cur = db.conn.cursor()
    table_name = RANDOM_STR

    db.create_title_to_ext_id_table(table_name)
    cur.execute(
        """SELECT Count() FROM sqlite_master
        WHERE type='table' and name='{}'"""
        .format(table_name)
    )
    if not cur.fetchone()[0] == 1:
        print(test_name, FAIL, 1)

    cols = cur.execute("PRAGMA table_info('{}')".format(table_name)).fetchall()
    if not cols[0] == (0, 'ext_id', 'TEXT', 0, None, 0):
        print(test_name, FAIL, 2)
    if not cols[1] == (1, 'title', 'TEXT', 0, None, 0):
        print(test_name, FAIL, 3)
    if not cols[2] == (2, 'year', 'INTEGER', 0, None, 0):
        print(test_name, FAIL, 4)
    if not cols[3] == (3, 'media_type', 'TEXT', 0, None, 0):
        print(test_name, FAIL, 5)

except Exception as e:
    print(test_name, FAIL, 6, e)

finally:
    db.close()

test_name = "Sqlite.create_title_to_ext_id_table dublicates"
print(test_name) if debug else ""
try:
    db = Sqlite()
    db.connect(TMP_DB)
    cur = db.conn.cursor()
    table_name = RANDOM_STR

    db.create_title_to_ext_id_table(table_name)
    db.create_title_to_ext_id_table(table_name)
    cur.execute(
        """SELECT Count() FROM sqlite_master
        WHERE type='table' and name='{}'"""
        .format(table_name)
    )
    if not cur.fetchone()[0] == 1:
        print(test_name, FAIL, 1)

except Exception as e:
    print(test_name, FAIL, 2, e)

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

    db.populate_title_to_ext_id_table(table_name, test_data)
    cur.execute(
        """SELECT Count() FROM {}
        WHERE ext_id='{}' AND title='{}' AND year={} AND media_type='{}'"""
        .format(table_name, ext_id, title, year, media_type))
    if not cur.fetchone()[0] == 1:
        print(test_name, FAIL, 1)

except Exception as e:
    print(test_name, FAIL, 2, e)

finally:
    db.close()

test_name = "Sqlite.populate_title_to_ext_id_table delete old data"
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

    db.populate_title_to_ext_id_table(table_name, test_data)
    cur.execute(
        """SELECT Count() FROM {}
        WHERE ext_id='{}' AND title='{}' AND year={} AND media_type='{}'"""
        .format(table_name, ext_id, title, year, media_type))
    if not cur.fetchone()[0] == 1:
        print(test_name, FAIL, 1)

    db.populate_title_to_ext_id_table(table_name, test_data)
    cur.execute(
        """SELECT Count() FROM {}
        WHERE ext_id='{}' AND title='{}' AND year={} AND media_type='{}'"""
        .format(table_name, ext_id, title, year, media_type))
    if not cur.fetchone()[0] == 1:
        print(test_name, FAIL, 2)

    db.populate_title_to_ext_id_table(table_name, [])
    cur.execute(
        """SELECT Count() FROM {}
        WHERE ext_id='{}' AND title='{}' AND year={} AND media_type='{}'"""
        .format(table_name, ext_id, title, year, media_type)
    )
    if not cur.fetchone()[0] == 0:
        print(test_name, FAIL, 3)

except Exception as e:
    print(test_name, FAIL, 4, e)

finally:
    db.close()

test_name = "db.create_title_to_anidb_id_table"
print(test_name) if debug else ""
try:
    db = Sqlite()
    db.connect(TMP_DB)
    cur = db.conn.cursor()

    db.create_title_to_anidb_id_table()
    cur.execute(
        """SELECT Count() FROM sqlite_master
        WHERE type='table' and name='{}'"""
        .format(Sqlite.TITLE_TO_ANIDB_ID)
    )
    if not cur.fetchone()[0] == 1:
        print(test_name, FAIL, 1)

except Exception as e:
    print(test_name, FAIL)

finally:
    db.close()

test_name = "Sqlite.populate_title_to_anidb_id_table"
print(test_name) if debug else ""
try:
    db = Sqlite()
    db.connect(TMP_DB)
    cur = db.conn.cursor()
    db.create_title_to_anidb_id_table()

    ext_id = RANDOM_STR
    title = RANDOM_STR
    year = RANDOM_INT
    media_type = RANDOM_STR
    test_data = [(ext_id, title, year, media_type)]

    db.populate_title_to_anidb_id_table(test_data)
    cur.execute(
        """SELECT Count() FROM {}
        WHERE ext_id='{}' AND title='{}' AND year={} AND media_type='{}'"""
        .format(Sqlite.TITLE_TO_ANIDB_ID, ext_id, title, year, media_type)
    )
    if not cur.fetchone()[0] == 1:
        print(test_name, FAIL, 1)

except Exception as e:
    print(test_name, FAIL, 2, e)

finally:
    db.close()

test_name = "db.create_title_to_imdb_id_table"
print(test_name) if debug else ""
try:
    db = Sqlite()
    db.connect(TMP_DB)
    cur = db.conn.cursor()

    db.create_title_to_imdb_id_table()

    cur.execute(
        """SELECT Count() FROM sqlite_master
        WHERE type='table' and name='{}'"""
        .format(Sqlite.TITLE_TO_IMDB_ID)
    )
    if not cur.fetchone()[0] == 1:
        print(test_name, FAIL, 1)

except Exception as e:
    print(test_name, FAIL)

finally:
    db.close()

test_name = "Sqlite.populate_title_to_imdb_id_table"
print(test_name) if debug else ""
try:
    db = Sqlite()
    db.connect(TMP_DB)
    cur = db.conn.cursor()
    db.create_title_to_imdb_id_table()

    ext_id = RANDOM_STR
    title = RANDOM_STR
    year = RANDOM_INT
    media_type = RANDOM_STR
    test_data = [(ext_id, title, year, media_type)]
    db.populate_title_to_imdb_id_table(test_data)

    cur.execute(
        """SELECT Count() FROM {}
        WHERE ext_id='{}' AND title='{}' AND year={} AND media_type='{}'"""
        .format(Sqlite.TITLE_TO_IMDB_ID, ext_id, title, year, media_type)
    )
    if not cur.fetchone()[0] == 1:
        print(test_name, FAIL, 1)

except Exception as e:
    print(test_name, FAIL, 2, e)

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

test_name = "Sqlite.get_anidb_ids"
print(test_name) if debug else ""
try:
    db = Sqlite()
    db.connect(TMP_DB)
    db.create_title_to_anidb_id_table()

    ext_id = RANDOM_STR
    title = RANDOM_STR
    year = RANDOM_INT
    media_type = RANDOM_STR
    test_data = [(ext_id, title, year, media_type)]
    db.populate_title_to_anidb_id_table(test_data)

    search_re = re.compile("^{}$".format(title))
    if (
        db.get_anidb_ids(search_re) !=
        db.get_ext_ids(Sqlite.TITLE_TO_ANIDB_ID, search_re)
    ):
        print(test_name, FAIL, 1)

except Exception as e:
    print(test_name, FAIL, 2, e)

finally:
    db.close()

test_name = "Sqlite.get_imdb_ids"
print(test_name) if debug else ""
try:
    db = Sqlite()
    db.connect(TMP_DB)
    db.create_title_to_imdb_id_table()

    ext_id = RANDOM_STR
    title = RANDOM_STR
    year = RANDOM_INT
    media_type = RANDOM_STR
    test_data = [(ext_id, title, year, media_type)]
    db.populate_title_to_imdb_id_table(test_data)

    search_re = re.compile("^{}$".format(title))
    if (
        db.get_imdb_ids(search_re) !=
        db.get_ext_ids(Sqlite.TITLE_TO_IMDB_ID, search_re)
    ):
        print(test_name, FAIL, 1)

except Exception as e:
    print(test_name, FAIL, 2, e)

finally:
    db.close()

print("db-sqlite-tests: Successfully Completed")
