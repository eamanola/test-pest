import sys
import os
sys.path.append(os.path.join(sys.path[0], '..'))
from classes.media import Media, Episode, Movie

debug = True;
debug = False;

RANDOM_STR = "foo"
RANDOM_STR2 = "bar"
RANDOM_INT = 22;
FAIL = "FAIL";
PASS = "PASS";

test_name = "isheritance:"
print(test_name) if debug else "";

test_name = "Media()"
print(test_name) if debug else "";

media = Media(RANDOM_STR);
if not isinstance(media, Media) or isinstance(media, Episode) or isinstance(media, Movie):
    print(test_name, FAIL);

test_name = "Episode()"
print(test_name) if debug else "";

episode = Episode(RANDOM_STR);
if not isinstance(episode, (Media, Episode)) or isinstance(episode, Movie):
    print(test_name, FAIL);

test_name = "Movie()"
print(test_name) if debug else "";

movie = Movie(RANDOM_STR);
if not isinstance(movie, (Media, Movie)) or isinstance(movie, Episode):
    print(test_name, FAIL);

test_name = "Media.media_name"
print(test_name) if debug else "";
media = Media(RANDOM_STR);
if not media.media_name == RANDOM_STR:
    print(test_name, FAIL);

test_name = "Media.file"
print(test_name) if debug else "";
media = Media(RANDOM_STR);
if not media.file == None:
    print(test_name, FAIL);

media = Media(RANDOM_STR);
media.file = RANDOM_STR2;
if not media.file == RANDOM_STR2:
    print(test_name, FAIL);

test_name = "Media.subtitles"
print(test_name) if debug else "";
media = Media(RANDOM_STR);
if not len(media.subtitles) == 0:
    print(test_name, FAIL);

media.subtitles.append(RANDOM_STR2);
if not len(media.subtitles) == 1:
    print(test_name, FAIL);


test_name = "Movie.year"
print(test_name) if debug else "";

movie = Movie(RANDOM_STR);
if not movie.year == None:
    print(test_name, FAIL);

movie.year = RANDOM_INT;
if not movie.year == RANDOM_INT:
    print(test_name, FAIL);

print("media-tests: Successfully Completed");
