import sys
import os
from classes.identifier import Identifier, AniDBIdentifier, IMDBIdentifier

debug = True;
debug = False;

RANDOM_STR = "foo"
RANDOM_STR2 = "bar"
RANDOM_INT = 22;
FAIL = "FAIL";
PASS = "PASS";

anidb_lines = [
    ("789", "JoJo no Kimyou na Bouken (2000)", 2000, ""),
    ("789", "JoJo no Kimyou na Bouken x", 0, ""),
    ("789", "JoJo no Kimyou na Bouken (2000)", 2000, ""),
    ("800", "JoJo no Kimyou na Bouken (2000)", 2000, "")
]

test_name = "AniDBIdentifier.filter_by_year"
print(test_name) if debug else "";
if not len(AniDBIdentifier().filter_by_year(anidb_lines, 2000)) == 3:
    print(test_name, FAIL, 1);

test_name = "AniDBIdentifier.filter_by_exact_match"
print(test_name) if debug else "";
if not len(AniDBIdentifier().filter_by_exact_match(anidb_lines, "JoJo no Kimyou na Bouken x")) == 1:
    print(test_name, FAIL, 1);

test_name = "AniDBIdentifier.filter_by_media_type"
print(test_name) if debug else "";
if not len(AniDBIdentifier().filter_by_media_type(anidb_lines, AniDBIdentifier.TV_SHOW)) == 0:
    print(test_name, FAIL, 1);

if not len(AniDBIdentifier().filter_by_media_type(anidb_lines, AniDBIdentifier.MOVIE)) == 0:
    print(test_name, FAIL, 2);

test_name = "AniDBIdentifier.group_by_id"
print(test_name) if debug else "";
if not len(AniDBIdentifier().group_by_id(anidb_lines)) == 2:
    print(test_name, FAIL, 1, len(AniDBIdentifier().group_by_id(anidb_lines)));

imdb_lines = [
    ("tt0000001", "Carmencita x", 1894, "movie"),
    ("tt0000001", "Carmencita", 1894, "tvEpisode"),
    ("tt0000001", "Carmencita", 0, "short"),
    ("tt0000002", "Carmencita", 1894, "short")
    #"tt0000001	movie	Carmencita x	Carmencita	0	1894	\\N	1	Documentary,Short",
    #"tt0000001	tvEpisode	Carmencita	Carmencita	0	1894	\\N	1	Documentary,Short",
    #"tt0000001	short	Carmencita	Carmencita	0	\\N	\\N	1	Documentary,Short",
    #"tt0000002	short	Carmencita	Carmencita	0	1894   \\N	1	Documentary,Short"
]

test_name = "IMDBIdentifier.filter_by_year"
if not len(IMDBIdentifier().filter_by_year(imdb_lines, 1894)) == 3:
    print(test_name, FAIL, 1);

test_name = "IMDBIdentifier.filter_by_exact_match"
print(test_name) if debug else "";
if not len(IMDBIdentifier().filter_by_exact_match(imdb_lines, "Carmencita x")) == 1:
    print(test_name, FAIL, 1);

test_name = "IMDBIdentifier.filter_by_media_type"
print(test_name) if debug else "";
if not len(IMDBIdentifier().filter_by_media_type(imdb_lines, IMDBIdentifier.TV_SHOW)) == 1:
    print(test_name, FAIL, 1, IMDBIdentifier().filter_by_media_type(imdb_lines, IMDBIdentifier.TV_SHOW));

if not len(IMDBIdentifier().filter_by_media_type(imdb_lines, IMDBIdentifier.MOVIE)) == 1:
    print(test_name, FAIL, 2);

test_name = "IMDBIdentifier.group_by_id"
print(test_name) if debug else "";
if not len(IMDBIdentifier().group_by_id(imdb_lines)) == 2:
    print(test_name, FAIL, 1);

test_name = "Identifier.compile_re_search"
print(test_name) if debug else "";
import re
test_str = "JoJo no Kimyou na-Bouken ova (2000) part 9 season 2 s2"
numbers_part_ova_season_and_s_special_chars_removed = "JoJo.+no.+Kimyou.+na.+Bouken"

if not Identifier.compile_re_search(test_str, True) == re.compile("^JoJo.+no.+Kimyou.+na.+Bouken$", re.IGNORECASE):
    print(test_name, FAIL, 1);

if not Identifier.compile_re_search(test_str, False) == re.compile(".*JoJo.+no.+Kimyou.+na.+Bouken.*", re.IGNORECASE):
    print(test_name, FAIL, 1);

print("identifier-tests: Successfully Completed");
