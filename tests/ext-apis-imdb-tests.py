from classes.ext_apis.imdb import Imdb_title_to_id_file_parser

debug = True
debug = False

RANDOM_STR = "foo"
RANDOM_STR2 = "bar"
RANDOM_INT = 22
FAIL = "FAIL"
PASS = "PASS"

test_name = "Imdb_title_to_id_file_parser.parse_title_from_line"
print(test_name) if debug else ""
if (
    Imdb_title_to_id_file_parser.parse_title_from_line(
        """tt0000001	short	Carmencita	Carmencita	0	1894	\\N	1
        Documentary,Short"""
    ) != "Carmencita"
):
    print(test_name, FAIL, 1)

test_name = "Imdb_title_to_id_file_parser.parse_id_from_line"
print(test_name) if debug else ""
if (
    Imdb_title_to_id_file_parser.parse_id_from_line(
        """tt0000001	short	Carmencita	Carmencita	0	1894	\\N	1
        Documentary,Short"""
    ) != "tt0000001"
):
    print(test_name, FAIL, 1)

test_name = "Imdb_title_to_id_file_parser.parse_year_from_line"
print(test_name) if debug else ""
tests = (
    ("""tt0000001	short	Carmencita	Carmencita	0	1894	\\N	1
        Documentary,Short""", 1894),
    ("""tt0000001	short	Carmencita	Carmencita	0	\\N	\\N	1
        Documentary,Short""", None),
    ("""tt0000001	short	Carmencita	Carmencita	0	189	\\N	1
        Documentary,Short""", None),
    ("""tt0000001	short	Carmencita	Carmencita	0	18943	\\N	1
        Documentary,Short""", None)
)
for test in tests:
    if Imdb_title_to_id_file_parser.parse_year_from_line(test[0]) != test[1]:
        print(test_name, FAIL, test[0], test[1])

test_name = "Imdb_title_to_id_file_parser.parse_media_type_from_line"
print(test_name) if debug else ""
if (
    Imdb_title_to_id_file_parser.parse_media_type_from_line(
        """tt0000001	short	Carmencita	Carmencita	0	1894	\\N	1
        Documentary,Short"""
    ) != "short"
):
    print(test_name, FAIL, 1)

print("ext_apis.imdb-tests: Successfully Completed")
