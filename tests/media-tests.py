import hashlib
from classes.media import Media, Episode, Movie

debug = True
debug = False

RANDOM_STR = "foo"
RANDOM_STR2 = "bar"
RANDOM_INT = 22
FILE_PATH = RANDOM_STR
EPISODE_NUMBER = RANDOM_INT
TITLE = RANDOM_STR
FAIL = "FAIL"
PASS = "PASS"

test_name = "isheritance:"
print(test_name) if debug else ""

test_name = "Media()"
print(test_name) if debug else ""

media = Media(FILE_PATH)
if (
    not isinstance(media, Media) or
    isinstance(media, Episode) or
    isinstance(media, Movie)
):
    print(test_name, FAIL)

test_name = "Episode()"
print(test_name) if debug else ""

episode = Episode(FILE_PATH, EPISODE_NUMBER)
if not isinstance(episode, (Media, Episode)) or isinstance(episode, Movie):
    print(test_name, FAIL)

test_name = "Movie()"
print(test_name) if debug else ""

movie = Movie(FILE_PATH, TITLE)
if not isinstance(movie, (Media, Movie)) or isinstance(movie, Episode):
    print(test_name, FAIL)

test_name = "Media.id"
print(test_name) if debug else ""
media = Media(FILE_PATH)
id = hashlib.md5(media.file_path().encode('utf-8')).hexdigest()
if media.id() != id:
    print(test_name, FAIL)

test_name = "Media.file_path"
print(test_name) if debug else ""
media = Media(FILE_PATH)
if media.file_path() != FILE_PATH:
    print(test_name, FAIL)

test_name = "Media.subtitles"
print(test_name) if debug else ""
media = Media(FILE_PATH)
if not len(media.subtitles) == 0:
    print(test_name, FAIL)

test_name = "Media.parent"
print(test_name) if debug else ""
media = Media(FILE_PATH)
if (
    media.parent() is not None and
    media._parent is not None
):
    print(test_name, FAIL, 1)

parent = RANDOM_STR
media = Media(FILE_PATH, parent)
if (
    not media.parent() == parent or
    not media.parent() == media._parent
):
    print(test_name, FAIL, 2)

test_name = "Episode.episode_number"
print(test_name) if debug else ""
episode = Episode(FILE_PATH, EPISODE_NUMBER)
if episode.episode_number() != EPISODE_NUMBER:
    print(test_name, FAIL)

test_name = "Movie.title"
print(test_name) if debug else ""
movie = Movie(FILE_PATH, TITLE)
if movie.title() != TITLE:
    print(test_name, FAIL)

media.subtitles.append(RANDOM_STR2)
if not len(media.subtitles) == 1:
    print(test_name, FAIL)

print("media-tests: Successfully Completed")
