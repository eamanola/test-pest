from metafinder.anidb import Anidb_title_to_id_file_parser

debug = True
debug = False

RANDOM_STR = "foo"
RANDOM_STR2 = "bar"
RANDOM_INT = 22
FAIL = "FAIL"
PASS = "PASS"

test_name = "Anidb_title_to_id_file_parser.parse_title_from_line"
print(test_name) if debug else ""
if (
    Anidb_title_to_id_file_parser.parse_title_from_line(
        "789|1|x-jat|JoJo no Kimyou na Bouken (2000)"
    ) !=
    "JoJo no Kimyou na Bouken (2000)"
):
    print(test_name, FAIL, 1)

test_name = "Anidb_title_to_id_file_parser.parse_id_from_line"
print(test_name) if debug else ""
if (
    Anidb_title_to_id_file_parser.parse_id_from_line(
        "789|1|x-jat|JoJo no Kimyou na Bouken (2000)"
    ) !=
    "789"
):
    print(test_name, FAIL, 1)

test_name = "Anidb_title_to_id_file_parser.parse_year_from_line"
print(test_name) if debug else ""
tests = (
    ("789|1|x-jat|JoJo no Kimyou na Bouken (2000)", 2000),
    ("789|1|x-jat|JoJo no Kimyou na Bouken (200)", None),
    ("789|1|x-jat|JoJo no Kimyou na Bouken (20000)", None),
    ("789|1|x-jat|JoJo no Kimyou na Bouken 2000", None)
)
for test in tests:
    if Anidb_title_to_id_file_parser.parse_year_from_line(test[0]) != test[1]:
        print(test_name, FAIL, test[0], test[1])

test_name = "Anidb_title_to_id_file_parser.parse_media_type_from_line"
print(test_name) if debug else ""
if (
    Anidb_title_to_id_file_parser.parse_media_type_from_line(
        "789|1|x-jat|JoJo no Kimyou na Bouken (2000)"
    ) is not None
):
    print(test_name, FAIL, 1)

print("ext_apis.anidb-tests: Successfully Completed")
