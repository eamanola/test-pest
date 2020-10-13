import sys
import os
from classes.file_name_parser import File_name_parser

debug = True
debug = False


def test_show_files(
    file_name,
    expected_show_name,
    expected_season,
    expected_episode,
    expected_year,
    expected_remove_user_tags,
    expected_remove_meta_tags,
    expected_remove_file_extension,
    expected_is_media,
    expected_is_subtitle,
    expected_is_oad,
    expected_is_extra,
    expected_is_ncop,
    expected_is_nced,
    expected_is_ova
):
    if File_name_parser.guess_show_name(file_name) != expected_show_name:
        print("guess_show_name:", file_name)
        print("expected:", '"%s"' % expected_show_name)
        print("got:", '"%s"' % File_name_parser.guess_show_name(file_name))
        print("--------------------------------------------------------------")

    if File_name_parser.guess_season(file_name) != expected_season:
        print("guess_season", file_name)
        print("expected:", expected_season)
        print("got:", File_name_parser.guess_season(file_name))
        print("--------------------------------------------------------------")

    if File_name_parser.guess_episode(file_name) != expected_episode:
        print("guess_episode", file_name)
        print("expected:", expected_episode)
        print("got:", File_name_parser.guess_episode(file_name))
        print("--------------------------------------------------------------")

    if File_name_parser.guess_year(file_name) != expected_year:
        print("guess_year:", file_name)
        print("expected:", expected_year)
        print("got:", File_name_parser.guess_year(file_name))
        print("--------------------------------------------------------------")

    if (File_name_parser.remove_user_tags(file_name)
            != expected_remove_user_tags):
        print("remove_user_tags:", file_name)
        print("expected:", '"%s"' % expected_remove_user_tags)
        print("got:", '"%s"' % File_name_parser.remove_user_tags(file_name))
        print("--------------------------------------------------------------")

    if (File_name_parser.remove_meta_tags(file_name)
            != expected_remove_meta_tags):
        print("remove_meta_tags:", file_name)
        print("expected:", '"%s"' % expected_remove_meta_tags)
        print("got:", '"%s"' % File_name_parser.remove_meta_tags(file_name))
        print("--------------------------------------------------------------")

    if (File_name_parser.remove_file_extension(file_name)
            != expected_remove_file_extension):
        print("remove_file_extension:", file_name)
        print("expected:", '"%s"' % expected_remove_file_extension)
        print("got:", '"%s"' % File_name_parser.remove_file_extension(
            file_name
        ))
        print("--------------------------------------------------------------")

    if (File_name_parser.is_media(file_name)
            != expected_is_media):
        print("is_media", file_name)
        print("expected:", expected_is_media)
        print("got:", File_name_parser.is_media(file_name))
        print("--------------------------------------------------------------")

    if File_name_parser.is_subtitle(file_name) != expected_is_subtitle:
        print("is_subtitle:", file_name)
        print("expected:", expected_is_subtitle)
        print("got:", File_name_parser.is_subtitle(file_name))
        print("--------------------------------------------------------------")

    if File_name_parser.is_oad(file_name) != expected_is_oad:
        print("is_oad:", file_name)
        print("expected:", expected_is_oad)
        print("got:", File_name_parser.is_oad(file_name))
        print("--------------------------------------------------------------")

    if File_name_parser.is_extra(file_name) != expected_is_extra:
        print("is_extra:", file_name)
        print("expected:", expected_is_extra)
        print("got:", File_name_parser.is_extra(file_name))
        print("--------------------------------------------------------------")

    if File_name_parser.is_ncop(file_name) != expected_is_ncop:
        print("is_ncop:", file_name)
        print("expected:", expected_is_ncop)
        print("got:", File_name_parser.is_ncop(file_name))
        print("--------------------------------------------------------------")

    if File_name_parser.is_nced(file_name) != expected_is_nced:
        print("is_nced:", file_name)
        print("expected:", expected_is_nced)
        print("got:", File_name_parser.is_nced(file_name))
        print("--------------------------------------------------------------")

    if File_name_parser.is_ova(file_name) != expected_is_ova:
        print("is_ova:", file_name)
        print("expected:", expected_is_ova)
        print("got:", File_name_parser.is_ova(file_name))
        print("--------------------------------------------------------------")


print('test_show_files:') if debug else ""
test_shows = open(os.path.join(sys.path[0], "test-shows"), "r")
line = test_shows.readline()

while line:
    if line.startswith('#'):
        print('-', line.strip()) if debug else ""
        line = test_shows.readline()
        continue
    elif not line.strip():
        print('-', line.strip()) if debug else ""
        line = test_shows.readline()
        continue
    elif line.strip() == "EOF":
        print('-', line.strip()) if debug else ""
        break

    # new test block
    file_name = line.strip()
    print('file_name:', file_name) if debug else ""

    line = test_shows.readline()
    expected_show_name = line.strip()
    print('expected_show_name:', expected_show_name) if debug else ""

    line = test_shows.readline()
    expected_season = int(line.strip())
    print('expected_season:', expected_season) if debug else ""

    line = test_shows.readline()
    expected_episode = int(line.strip())
    print('expected_episode:', expected_episode) if debug else ""

    line = test_shows.readline()
    expected_year = int(line.strip())
    print('expected_year:', expected_year) if debug else ""

    line = test_shows.readline()
    expected_remove_user_tags = line.strip()
    print(
        'expected_remove_user_tags:',
        expected_remove_user_tags
    ) if debug else ""

    line = test_shows.readline()
    expected_remove_meta_tags = line.strip()
    print(
        'expected_remove_meta_tags:',
        expected_remove_meta_tags
    ) if debug else ""

    line = test_shows.readline()
    expected_remove_file_extension = line.strip()
    print(
        'expected_remove_file_extension:',
        expected_remove_file_extension
    ) if debug else ""

    line = test_shows.readline()
    expected_is_media = line.strip().lower() == "true"
    print('expected_is_media:', expected_is_media) if debug else ""

    line = test_shows.readline()
    expected_is_subtitle = line.strip().lower() == "true"
    print('expected_is_subtitle:', expected_is_subtitle) if debug else ""

    line = test_shows.readline()
    expected_is_oad = line.strip().lower() == "true"
    print('expected_is_oad:', expected_is_oad) if debug else ""

    line = test_shows.readline()
    expected_is_extra = line.strip().lower() == "true"
    print('expected_is_extra:', expected_is_extra) if debug else ""

    line = test_shows.readline()
    expected_is_ncop = line.strip().lower() == "true"
    print('expected_is_ncop:', expected_is_ncop) if debug else ""

    line = test_shows.readline()
    expected_is_nced = line.strip().lower() == "true"
    print('expected_is_nced:', expected_is_nced) if debug else ""

    line = test_shows.readline()
    expected_is_ova = line.strip().lower() == "true"
    print('expected_is_ova:', expected_is_ova) if debug else ""

    test_show_files(
        file_name,
        expected_show_name,
        expected_season,
        expected_episode,
        expected_year,
        expected_remove_user_tags,
        expected_remove_meta_tags,
        expected_remove_file_extension,
        expected_is_media,
        expected_is_subtitle,
        expected_is_oad,
        expected_is_extra,
        expected_is_ncop,
        expected_is_nced,
        expected_is_ova
    )

    line = test_shows.readline()

test_shows.close()

print("") if debug else ""


def test_movie_files(
    file_name,
    expected_show_name,
    expected_year
):
    if File_name_parser.guess_show_name(file_name) != expected_show_name:
        print('guess_show_name', file_name)
        print('expected', '"%s"' % expected_show_name)
        print('got', '"%s"' % File_name_parser.guess_show_name(file_name))
        print("--------------------------------------------------------------")

    if File_name_parser.guess_year(file_name) != expected_year:
        print('guess_year', file_name)
        print('expected', expected_year)
        print('got', File_name_parser.guess_year(file_name))
        print("--------------------------------------------------------------")


print('test_movie_files:') if debug else ""
test_movies = open(os.path.join(sys.path[0], "test-movies"), "r")
line = test_movies.readline()

while line:
    if line.startswith('#'):
        print('-', line.strip()) if debug else ""
        line = test_movies.readline()
        continue
    elif not line.strip():
        print('-', line.strip()) if debug else ""
        line = test_movies.readline()
        continue
    elif line.strip() == "EOF":
        print('-', line.strip()) if debug else ""
        break

    file_name = line.strip()
    print('file_name:', file_name) if debug else ""
    line = test_movies.readline()

    expected_show_name = line.strip()
    print('expected_show_name:', expected_show_name) if debug else ""
    line = test_movies.readline()

    expected_year = int(line.strip())
    print('expected_year:', expected_year) if debug else ""
    line = test_movies.readline()

    test_movie_files(
        file_name,
        expected_show_name,
        expected_year
    )

test_movies.close()

print("") if debug else ""

print('guess_season unit:') if debug else ""
season_test = (
    'show/Season 1/e1.mkv',
    'show/Season1/e1.mkv',
    'show/Season.1/e1.mkv',
    'show/S 1/e1.mkv',
    'show/S1/e1.mkv',
    'show/S.1/e1.mkv'
)
for test in season_test:
    print(test) if debug else ""

    if File_name_parser.guess_season(test) != 1:
        print('guess_season', test)
        print('expected', 1)
        print('got', File_name_parser.guess_season(test))

print("") if debug else ""

print('guess_episode unit:') if debug else ""
episode_test = (
    'show/Season 1/episode 1.mkv',
    'show/Season 1/episode1.mkv',
    'show/Season 1/episode.1.mkv',
    'show/Season 1/e 1.mkv',
    'show/Season 1/e1.mkv',
    'show/Season 1/e.1.mkv'
)
for test in episode_test:
    print(test) if debug else ""

    if File_name_parser.guess_episode(test) != 1:
        print('guess_episode', test)
        print('expected', 1)
        print('got', File_name_parser.guess_episode(test))

print("") if debug else ""

print('is_extra & episode:') if debug else ""
extras_test = (
    'show/extras/episode 1.mkv',
    'show/Season1/extra1.mkv',
    'show/Season1/extra 1.mkv',
    'show/Season1/extra.1.mkv'
)
for test in extras_test:
    print(test) if debug else ""

    if File_name_parser.guess_episode(test) != 1:
        print('extras_test', test)
        print('expected', 1)
        print('got', File_name_parser.guess_episode(test))

    if not File_name_parser.is_extra(test):
        print('extras_test', test)
        print('expected extra')
        print('got not')

print("") if debug else ""

print('is_extra case sensitivity small:') if debug else ""
test = 'show/Season1/extra1.mkv'
print(test) if debug else ""
if not File_name_parser.is_extra(test):
    print('is_extra case sensitivity small:', test)
    print('expected extra')
    print('got not')

print("") if debug else ""

print('is_extra case sensitivity mixed:') if debug else ""
test = 'show/Season1/ExTRa1.mkv'
print(test) if debug else ""
if not File_name_parser.is_extra(test):
    print('is_extra case sensitivity mixed:', test)
    print('expected extra')
    print('got not')

print("") if debug else ""

print('is_extra case sensitivity capital:') if debug else ""
test = 'show/Season1/EXTRA1.mkv'
print(test) if debug else ""
if not File_name_parser.is_extra(test):
    print('is_extra case sensitivity capital:', test)
    print('expected extra')
    print('got not')

print("") if debug else ""

print('is_oad & episode:') if debug else ""
oad_test = (
    'show/OAD/episode 1.mkv',
    'show/Season1/OAD1.mkv',
    'show/Season1/OAD 1.mkv',
    'show/Season1/OAD.1.mkv'
)
for test in oad_test:
    print(test) if debug else ""

    if File_name_parser.guess_episode(test) != 1:
        print('oad_test', test)
        print('expected', 1)
        print('got', File_name_parser.guess_episode(test))

    if not File_name_parser.is_oad(test):
        print('oad_test', test)
        print('expected OAD')
        print('got not')

print("") if debug else ""

print('is_oad case sensitivity small:') if debug else ""
test = 'show/Season1/oad1.mkv'
print(test) if debug else ""
if File_name_parser.is_oad(test):
    print('is_oad case sensitivity small:', test)
    print('expected not OAD')
    print('got OAD')

print("") if debug else ""

print('is_oad case sensitivity mixed:') if debug else ""
test = 'show/Season1/oAd1.mkv'
print(test) if debug else ""
if File_name_parser.is_oad(test):
    print('oad_test case sensitivity mixed', test)
    print('expected not OAD')
    print('got OAD')

print("") if debug else ""

print('is_oad case sensitivity capital:') if debug else ""
test = 'show/Season1/OAD1.mkv'
print(test) if debug else ""
if not File_name_parser.is_oad(test):
    print('is_oad case sensitivity capital', test)
    print('expected OAD')
    print('got not')

print("") if debug else ""

print('is_ncop & episode:') if debug else ""
ncop_test = (
    'show/NCOP/episode 1.mkv',
    'show/Season1/NCOP1.mkv',
    'show/Season1/NCOP 1.mkv',
    'show/Season1/NCOP.1.mkv'
)
for test in ncop_test:
    print(test) if debug else ""

    if File_name_parser.guess_episode(test) != 1:
        print('ncop_test', test)
        print('expected', 1)
        print('got', File_name_parser.guess_episode(test))

    if not File_name_parser.is_ncop(test):
        print('ncop_test', test)
        print('expected NCOP')
        print('got not')

print('is_ncop case sensitivity small:') if debug else ""
test = 'show/Season1/ncop1.mkv'
print(test) if debug else ""
if File_name_parser.is_ncop(test):
    print('is_ncop case sensitivity small:', test)
    print('expected not NCOP')
    print('got NCOP')

print("") if debug else ""

print('is_ncop case sensitivity mixed:') if debug else ""
test = 'show/Season1/nCOp1.mkv'
print(test) if debug else ""
if File_name_parser.is_ncop(test):
    print('is_ncop case sensitivity mixed', test)
    print('expected not NCOP')
    print('got NCOP')

print("") if debug else ""

print('is_ncop case sensitivity capital:') if debug else ""
test = 'show/Season1/NCOP1.mkv'
print(test) if debug else ""
if not File_name_parser.is_ncop(test):
    print('is_ncop case sensitivity capital', test)
    print('expected NCOP')
    print('got not')

print("") if debug else ""

print('is_nced & episode:') if debug else ""
nced_test = (
    'show/NCED/episode 1.mkv',
    'show/Season1/NCED1.mkv',
    'show/Season1/NCED 1.mkv',
    'show/Season1/NCED.1.mkv'
)
for test in nced_test:
    print(test) if debug else ""

    if File_name_parser.guess_episode(test) != 1:
        print('nced_test', test)
        print('expected', 1)
        print('got', File_name_parser.guess_episode(test))

    if not File_name_parser.is_nced(test):
        print('nced_test', test)
        print('expected NCOP')
        print('got not')

print('is_nced case sensitivity small:') if debug else ""
test = 'show/Season1/nced1.mkv'
print(test) if debug else ""
if File_name_parser.is_nced(test):
    print('is_nced case sensitivity small:', test)
    print('expected not NCED')
    print('got NCED')

print("") if debug else ""

print('is_nced case sensitivity mixed:') if debug else ""
test = 'show/Season1/Nced1.mkv'
print(test) if debug else ""
if File_name_parser.is_nced(test):
    print('id_nced case sensitivity mixed', test)
    print('expected not NCED')
    print('got NCED')

print("") if debug else ""

print('is_nced case sensitivity capital:') if debug else ""
test = 'show/Season1/NCED1.mkv'
print(test) if debug else ""
if not File_name_parser.is_nced(test):
    print('is_nced case sensitivity capital', test)
    print('expected NCED')
    print('got not')

print("") if debug else ""

print("file-name-parser-tests: Successfully Completed")
