import re
from classes.identifier import Identifier, AniDBIdentifier, IMDBIdentifier

debug = True
debug = False

RANDOM_STR = "foo"
RANDOM_STR2 = "bar"
RANDOM_INT = 22
FAIL = "FAIL"
PASS = "PASS"

anidb_lines = [
    ("789", "JoJo no Kimyou na Bouken (2000)", 2000, ""),
    ("789", "JoJo no Kimyou na Bouken x", 0, ""),
    ("789", "JoJo no Kimyou na Bouken (2000)", 2000, ""),
    ("800", "JoJo no Kimyou na Bouken (2000)", 2000, "")
]

test_name = "AniDBIdentifier.filter_by_year"
print(test_name) if debug else ""
if not len(AniDBIdentifier().filter_by_year(anidb_lines, 2000)) == 3:
    print(test_name, FAIL, 1)

test_name = "AniDBIdentifier.filter_by_exact_match"
print(test_name) if debug else ""
if (
    len(AniDBIdentifier().filter_by_exact_match(
        anidb_lines,
        "JoJo no Kimyou na Bouken x"
    )) != 1
):
    print(test_name, FAIL, 1)

test_name = "AniDBIdentifier.filter_by_media_type"
print(test_name) if debug else ""
if (
    len(AniDBIdentifier().filter_by_media_type(
        anidb_lines,
        AniDBIdentifier.TV_SHOW
    )) != 0
):
    print(test_name, FAIL, 1)

if (
    len(AniDBIdentifier().filter_by_media_type(
        anidb_lines,
        AniDBIdentifier.MOVIE
    )) != 0
):
    print(test_name, FAIL, 2)

test_name = "AniDBIdentifier.group_by_id"
print(test_name) if debug else ""
if not len(AniDBIdentifier().group_by_id(anidb_lines)) == 2:
    print(test_name, FAIL, 1, len(AniDBIdentifier().group_by_id(anidb_lines)))

imdb_lines = [
    ("tt0000001", "Carmencita x", 1894, "movie"),
    ("tt0000001", "Carmencita", 1894, "tvEpisode"),
    ("tt0000001", "Carmencita", 0, "short"),
    ("tt0000002", "Carmencita", 1894, "short")
]

test_name = "IMDBIdentifier.filter_by_year"
if not len(IMDBIdentifier().filter_by_year(imdb_lines, 1894)) == 3:
    print(test_name, FAIL, 1)

test_name = "IMDBIdentifier.filter_by_exact_match"
print(test_name) if debug else ""
if (
    len(IMDBIdentifier().filter_by_exact_match(
        imdb_lines,
        "Carmencita x"
    )) != 1
):
    print(test_name, FAIL, 1)

test_name = "IMDBIdentifier.filter_by_media_type"
print(test_name) if debug else ""
if (
    len(IMDBIdentifier().filter_by_media_type(
        imdb_lines,
        IMDBIdentifier.TV_SHOW
    )) != 1
):
    print(
        test_name, FAIL,
        1,
        IMDBIdentifier().filter_by_media_type(
            imdb_lines,
            IMDBIdentifier.TV_SHOW
        )
    )

if (
    len(IMDBIdentifier().filter_by_media_type(
        imdb_lines,
        IMDBIdentifier.MOVIE
    )) != 1
):
    print(test_name, FAIL, 2)

test_name = "IMDBIdentifier.group_by_id"
print(test_name) if debug else ""
if not len(IMDBIdentifier().group_by_id(imdb_lines)) == 2:
    print(test_name, FAIL, 1)

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
