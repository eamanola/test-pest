import re
from classes.identifier import Identifier
from classes.dbs.sqlite import Sqlite
from classes.ext_api import Ext_api

debug = True
debug = False

RANDOM_STR = "foo"
RANDOM_STR2 = "bar"
RANDOM_INT = 22
FAIL = "FAIL"
PASS = "PASS"

test_lines = [
    ("789", "JoJo no Kimyou na Bouken (2000)", 2000, "movie"),
    ("789", "JoJo no Kimyou na Bouken x", 0, "tvEpisode"),
    ("789", "JoJo no Kimyou na Bouken (2000)", 2000, "short"),
    ("800", "JoJo no Kimyou na Bouken (2000)", 2000, "")
]

test_name = "Identifier.filter_by_year"
print(test_name) if debug else ""
if not len(Identifier.filter_by_year(test_lines, 2000)) == 3:
    print(test_name, FAIL, 1)

test_name = "Identifier.filter_by_exact_match"
print(test_name) if debug else ""
if (
    len(Identifier.filter_by_exact_match(
        test_lines,
        "JoJo no Kimyou na Bouken x"
    )) != 1
):
    print(test_name, FAIL, 1)

test_name = "Identifier.filter_by_media_type"
print(test_name) if debug else ""
if (
    len(Identifier.filter_by_media_type(
        test_lines,
        "movie"
    )) != 1
):
    print(test_name, FAIL, 1)

if (
    len(Identifier.filter_by_media_type(
        test_lines,
        "tvEpisode"
    )) != 1
):
    print(test_name, FAIL, 2)

test_name = "Identifier.compile_re_search"
print(test_name) if debug else ""
test_str = "JoJo no Kimyou na-Bouken ova (2000) part 9 season 2 s2"

if (
    Identifier.compile_re_search(test_str, True) !=
    re.compile("^JoJo.+no.+Kimyou.+na.+Bouken$", re.IGNORECASE)
):
    print(test_name, FAIL, 1)

if (
    Identifier.compile_re_search(test_str, False) !=
    re.compile(".*JoJo.+no.+Kimyou.+na.+Bouken.*", re.IGNORECASE)
):
    print(test_name, FAIL, 1)

test_name = "Identifier.search_db"
print(test_name) if debug else ""
try:
    db = Sqlite()
    db.connect(":memory:")
    table_name = RANDOM_STR

    ext_id = RANDOM_STR
    title = RANDOM_STR
    year = RANDOM_INT
    media_type = RANDOM_STR
    test_data = [
        (ext_id, title, year, media_type),
        (ext_id + RANDOM_STR, title + RANDOM_STR, year, media_type),
        (ext_id + RANDOM_STR2, title[::-1], year, media_type)
    ]
    db.populate_title_to_ext_id_table(table_name, test_data)

    ext_api = Ext_api()
    ext_api.TITLE_TO_ID_TABLE = table_name

    identifier = Identifier(ext_api)

    show_name = title
    if len(identifier.search_db(db, show_name)) != 2:
        print(test_name, FAIL, 1)

    show_name = title[::-1]
    if len(identifier.search_db(db, show_name)) == 1:
        print(test_name, FAIL, 2)

    show_name = title + RANDOM_STR
    if identifier.search_db(db, show_name)[0] != test_data[1]:
        print(test_name, FAIL, 3)

    show_name = title + RANDOM_STR2
    if not len(identifier.search_db(db, show_name)) == 0:
        print(test_name, FAIL, 4)

except Exception as e:
    print(test_name, FAIL, 5, e)

finally:
    db.close()

print("identifier-tests: Successfully Completed")
