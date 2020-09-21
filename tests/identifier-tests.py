import re
from classes.identifier import Identifier

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

print("identifier-tests: Successfully Completed")
