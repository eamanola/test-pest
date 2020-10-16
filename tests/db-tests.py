from classes.db import DB
from classes.dbs.sqlite import Sqlite

debug = True
debug = False

RANDOM_STR = "foo"
RANDOM_STR2 = "bar"
RANDOM_INT = 22
FAIL = "FAIL"
PASS = "PASS"

test_name = "db.connect"
print(test_name) if debug else ""
try:
    DB().connect()
    print(test_name, FAIL)
except NotImplementedError as e:
    pass

test_name = "db.close"
print(test_name) if debug else ""
try:
    DB().close()
    print(test_name, FAIL)
except NotImplementedError as e:
    pass

test_name = "db.populate_title_to_ext_id_table"
print(test_name) if debug else ""
try:
    DB().populate_title_to_ext_id_table(RANDOM_STR, RANDOM_STR)
    print(test_name, FAIL)
except NotImplementedError as e:
    pass

test_name = "db.get_ext_ids"
print(test_name) if debug else ""
try:
    DB().get_ext_ids(RANDOM_STR, RANDOM_STR)
    print(test_name, FAIL)
except NotImplementedError as e:
    pass

test_name = "db.get_instance"
print(test_name) if debug else ""
DB.db_type = RANDOM_STR
try:
    db = DB.get_instance()
    print(test_name, FAIL, 1)
except NotImplementedError as e:
    pass

DB.db_type = DB.MARIADB
try:
    db = DB.get_instance()
    print(test_name, FAIL, 2)
except NotImplementedError as e:
    pass

DB.db_type = DB.MYSQL
try:
    db = DB.get_instance()
    print(test_name, FAIL, 3)
except NotImplementedError as e:
    pass

DB.db_type = DB.SQLITE
db = DB.get_instance()
if not isinstance(db, Sqlite):
    print(test_name, FAIL, 4)

test_name = "db.create_containers_table"
print(test_name) if debug else ""
try:
    DB().create_containers_table()
    print(test_name, FAIL)
except NotImplementedError as e:
    pass

test_name = "db.update_containers"
print(test_name) if debug else ""
try:
    DB().update_containers(RANDOM_STR)
    print(test_name, FAIL)
except NotImplementedError as e:
    pass

test_name = "db.get_container"
print(test_name) if debug else ""
try:
    DB().get_container(RANDOM_STR)
    print(test_name, FAIL)
except NotImplementedError as e:
    pass

test_name = "db.delete_containers"
print(test_name) if debug else ""
try:
    DB().delete_containers(RANDOM_STR)
    print(test_name, FAIL)
except NotImplementedError as e:
    pass

test_name = "db.create_media_table"
print(test_name) if debug else ""
try:
    DB().create_media_table()
    print(test_name, FAIL, 1)
except NotImplementedError as e:
    pass

test_name = "db.update_media"
print(test_name) if debug else ""
try:
    DB().update_media(RANDOM_STR)
    print(test_name, FAIL)
except NotImplementedError as e:
    pass

test_name = "db.get_media"
print(test_name) if debug else ""
try:
    DB().get_media(RANDOM_STR)
    print(test_name, FAIL)
except NotImplementedError as e:
    pass

test_name = "db.delete_media"
print(test_name) if debug else ""
try:
    DB().delete_media(RANDOM_STR)
    print(test_name, FAIL)
except NotImplementedError as e:
    pass


print("db-tests: Successfully Completed")
