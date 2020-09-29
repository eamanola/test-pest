import os
import shutil
from pathlib import Path
from classes.scanner import Scanner
from classes.container import MediaLibrary, Show, Season, Extra
from classes.media import Episode, Movie

debug = True
debug = False

RANDOM_STR = "foo"
RANDOM_STR2 = "bar"
RANDOM_INT = 22
FAIL = "FAIL"
PASS = "PASS"

TEST_LIBRARY_PATH = "/tmp/scanner-tests/"

test_files = [
    os.path.join(TEST_LIBRARY_PATH, "movie.mkv"),
    os.path.join(TEST_LIBRARY_PATH, "random.txt"),
    os.path.join(TEST_LIBRARY_PATH, "Show 1", "episode 1.mkv"),
    os.path.join(TEST_LIBRARY_PATH, "Show 1", "S02E2.mkv"),
    os.path.join(TEST_LIBRARY_PATH, "Show 2", "Season1", "some file 1.mkv"),
    os.path.join(
        TEST_LIBRARY_PATH,
        "Show 2",
        "Season2",
        "extra",
        "other file 1.mkv"
    )
]

for test_file in test_files:
    print(file_name) if debug else ""

    path = Path(test_file)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.touch(exist_ok=True)

test_name = "Scanner.ls_path"
print(test_name) if debug else ""
file_paths = Scanner.ls_path(TEST_LIBRARY_PATH)
if len(file_paths) != len(test_files):
    print(test_name, FAIL)

test_name = "Scanner.filter_types"
print(test_name) if debug else ""
file_paths = Scanner.ls_path(TEST_LIBRARY_PATH)
file_paths = Scanner.filter_types(file_paths)
if len(file_paths) != len(test_files) - 1:
    print(test_name, FAIL)

test_name = "Scanner.filter_media_library"
print(test_name) if debug else ""
file_paths = Scanner.filter_media_library(MediaLibrary(TEST_LIBRARY_PATH))
if len(file_paths) != len(test_files) - 1:
    print(test_name, FAIL)

test_name = "Scanner.filter_show"
print(test_name) if debug else ""
file_paths = Scanner.filter_show(Show(TEST_LIBRARY_PATH, "Show 1"))
if len(file_paths) != 2:
    print(test_name, FAIL)

test_name = "Scanner.filter_show"
print(test_name) if debug else ""
file_paths = Scanner.filter_season(Season(TEST_LIBRARY_PATH, "Show 1", 1))
if len(file_paths) != 0:
    print(test_name, FAIL)

file_paths = Scanner.filter_season(Season(TEST_LIBRARY_PATH, "Show 1", 2))
if len(file_paths) != 1:
    print(test_name, FAIL)

test_name = "Scanner.filter_extra"
file_paths = Scanner.filter_extra(Extra(TEST_LIBRARY_PATH, "Show 1", 2))
if len(file_paths) != 0:
    print(test_name, FAIL)

file_paths = Scanner.filter_extra(Extra(TEST_LIBRARY_PATH, "Show 2", 1))
if len(file_paths) != 0:
    print(test_name, FAIL)

file_paths = Scanner.filter_extra(Extra(TEST_LIBRARY_PATH, "Show 2", 2))
if len(file_paths) != 1:
    print(test_name, FAIL)

test_name = "Scanner.scan_media_library"
print(test_name) if debug else ""
media_library = MediaLibrary(TEST_LIBRARY_PATH)
if len(media_library.containers) != 0 or len(media_library.media) != 0:
    print(test_name, FAIL)
Scanner.scan_media_library(media_library)
if len(media_library.containers) != 2 or len(media_library.media) != 1:
    print(test_name, FAIL)

test_name = "Scanner.scan_show"
print(test_name) if debug else ""
show = Show(TEST_LIBRARY_PATH, "Show 2")
if len(show.containers) != 0 or len(show.media) != 0:
    print(test_name, FAIL, 1)
show = Scanner.scan_show(show)
if len(show.containers) != 2 or len(show.media) != 0:
    print(test_name, FAIL, 2)
show = Show(TEST_LIBRARY_PATH, "Show 1")
show = Scanner.scan_show(show)
if len(show.containers) != 1 or len(show.media) != 1:
    print(test_name, FAIL, 3)

test_name = "Scanner.scan_season"
print(test_name) if debug else ""
season = Season(TEST_LIBRARY_PATH, "Show 2", 2)
if len(season.containers) != 0 or len(season.media) != 0:
    print(test_name, FAIL, 1)
season = Scanner.scan_season(season)
if len(season.containers) != 1 or len(season.media) != 0:
    print(test_name, FAIL, 2)
season = Season(TEST_LIBRARY_PATH, "Show 1", 2)
season = Scanner.scan_season(season)
if len(season.containers) != 0 or len(season.media) != 1:
    print(test_name, FAIL, 3)

test_name = "Scanner.scan_extra"
print(test_name) if debug else ""
extra = Extra(TEST_LIBRARY_PATH, "Show 2", 2)
if len(extra.containers) != 0 or len(extra.media) != 0:
    print(test_name, FAIL, 1)
extra = Scanner.scan_extra(extra)
if len(extra.containers) != 0 or len(extra.media) != 1:
    print(test_name, FAIL, 2)
extra = Extra(TEST_LIBRARY_PATH, "Show 1", 2)
extra = Scanner.scan_extra(extra)
if extra is not None:
    print(test_name, FAIL, 3)

shutil.rmtree(TEST_LIBRARY_PATH)
print("scanner-tests: Successfully Completed")
