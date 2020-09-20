from classes.db import DB
from classes.dbs.sqlite import Sqlite

debug = True;
debug = False;

RANDOM_STR = "foo"
RANDOM_STR2 = "bar"
RANDOM_INT = 22;
FAIL = "FAIL";
PASS = "PASS";

test_name = "db.connect"
print(test_name) if debug else "";
try:
    DB().connect()
    print(test_name, FAIL);
except Exception as e:
    if not isinstance(e, NotImplementedError):
        print(test_name, FAIL);

test_name = "db.close"
print(test_name) if debug else "";
try:
    DB().close()
    print(test_name, FAIL);
except Exception as e:
    if not isinstance(e, NotImplementedError):
        print(test_name, FAIL);

test_name = "db.create_title_to_anidb_id_table"
print(test_name) if debug else "";
try:
    DB().create_title_to_anidb_id_table()
    print(test_name, FAIL);
except Exception as e:
    if not isinstance(e, NotImplementedError):
        print(test_name, FAIL);

test_name = "db.populate_title_to_anidb_id_table"
print(test_name) if debug else "";
try:
    DB().populate_title_to_anidb_id_table(RANDOM_STR)
    print(test_name, FAIL);
except Exception as e:
    if not isinstance(e, NotImplementedError):
        print(test_name, FAIL);

test_name = "db.create_title_to_imdb_id_table"
print(test_name) if debug else "";
try:
    DB().create_title_to_imdb_id_table()
    print(test_name, FAIL);
except Exception as e:
    if not isinstance(e, NotImplementedError):
        print(test_name, FAIL);

test_name = "db.populate_title_to_imdb_id_table"
print(test_name) if debug else "";
try:
    DB().populate_title_to_imdb_id_table(RANDOM_STR)
    print(test_name, FAIL);
except Exception as e:
    if not isinstance(e, NotImplementedError):
        print(test_name, FAIL);

test_name = "db.get_anidb_ids"
print(test_name) if debug else "";
try:
    DB().get_anidb_ids(RANDOM_STR)
    print(test_name, FAIL);
except Exception as e:
    if not isinstance(e, NotImplementedError):
        print(test_name, FAIL);

test_name = "db.get_imdb_ids"
print(test_name) if debug else "";
try:
    DB().get_imdb_ids(RANDOM_STR)
    print(test_name, FAIL);
except Exception as e:
    if not isinstance(e, NotImplementedError):
        print(test_name, FAIL);

test_name = "db.get_instance"
print(test_name) if debug else "";
DB.db_type = RANDOM_STR;
db = DB().get_instance()
if db != None:
    print(test_name, FAIL, 1);

DB.db_type = DB.MARIADB;
try:
    db = DB().get_instance()
    print(test_name, FAIL, 2);
except Exception as e:
    if not isinstance(e, NotImplementedError):
        print(test_name, FAIL);

DB.db_type = DB.MYSQL;
try:
    db = DB().get_instance()
    print(test_name, FAIL, 3);
except Exception as e:
    if not isinstance(e, NotImplementedError):
        print(test_name, FAIL);

DB.db_type = DB.SQLITE;
db = DB().get_instance()
if not isinstance(db, Sqlite):
    print(test_name, FAIL, 4);

print("db-tests: Successfully Completed");
