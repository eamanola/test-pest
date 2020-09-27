from classes.container import Container, MediaLibrary, Show, Season, Extra
from classes.media import Media

debug = True
debug = False

RANDOM_STR = "foo"
RANDOM_STR2 = "bar"
RANDOM_INT = 22
FAIL = "FAIL"
PASS = "PASS"

LIBRARY_PATH = RANDOM_STR
SHOW_NAME = RANDOM_STR2
SEASON_NUMBER = RANDOM_INT

test_name = "isheritance:"
print(test_name) if debug else ""

test_name = "Container()"
print(test_name) if debug else ""

container = Container()
if (
    not isinstance(container, Container) or
    isinstance(container, MediaLibrary) or
    isinstance(container, Show) or
    isinstance(container, Season) or
    isinstance(container, Extra)
):
    print(test_name, FAIL)

test_name = "MediaLibrary()"
print(test_name) if debug else ""

mediaLibrary = MediaLibrary(LIBRARY_PATH)
if (
    not isinstance(mediaLibrary, (Container, MediaLibrary)) or
    isinstance(mediaLibrary, Show) or
    isinstance(mediaLibrary, Season) or
    isinstance(mediaLibrary, Extra)
):
    print(test_name, FAIL)

test_name = "Show()"
print(test_name) if debug else ""

show = Show(LIBRARY_PATH, SHOW_NAME)
if (
    not isinstance(show, (Container, MediaLibrary, Show)) or
    isinstance(container, Season) or
    isinstance(container, Extra)
):
    print(test_name, FAIL)

test_name = "Season()"
print(test_name) if debug else ""

season = Season(LIBRARY_PATH, SHOW_NAME, SEASON_NUMBER)
if (
    not isinstance(season, (Container, MediaLibrary, Show, Season)) or
    isinstance(container, Extra)
):
    print(test_name, FAIL)

test_name = "Extra()"
print(test_name) if debug else ""

extra = Extra(LIBRARY_PATH, SHOW_NAME, SEASON_NUMBER)
if not isinstance(extra, (Container, MediaLibrary, Show, Season, Extra)):
    print(test_name, FAIL)

test_name = "Container.get_container"
print(test_name) if debug else ""

container = MediaLibrary(LIBRARY_PATH)

if container.get_container(RANDOM_STR) is not None:
    print(test_name, FAIL, 1)

container2 = Show(LIBRARY_PATH, SHOW_NAME)
container.containers.append(container2)
if not container.get_container(container2.id()) == container2:
    print(test_name, FAIL, 2)

if container.get_container(RANDOM_STR) is not None:
    print(test_name, FAIL, 3)

test_name = "Container.get_media"
print(test_name) if debug else ""
container = Container()

media = Media(RANDOM_STR2)
container.media.append(media)

if not container.get_media(media.id()) == media:
    print(test_name, FAIL, 2)

if container.get_media(RANDOM_STR) is not None:
    print(test_name, FAIL, 3)

test_name = "Container.parent"
print(test_name) if debug else ""
container = Container()
if (
    container.parent() is not None and
    container._parent is not None
):
    print(test_name, FAIL)

parent = Container()
container = Container(parent=parent)
if (
    not container.parent() == parent or
    not container.parent() == container._parent
):
    print(test_name, FAIL)

test_name = "MediaLibrary.path()"
print(test_name) if debug else ""
mediaLibrary = MediaLibrary(LIBRARY_PATH)
if (
    not mediaLibrary.path() == LIBRARY_PATH or
    not mediaLibrary.path() == mediaLibrary._path
):
    print(test_name, FAIL)

test_name = "Show.show_name"
print(test_name) if debug else ""
show = Show(LIBRARY_PATH, SHOW_NAME)
if (
    not show.show_name() == SHOW_NAME or
    not show.show_name() == show._show_name
):
    print(test_name, FAIL)

test_name = "Show.seasons"
print(test_name) if debug else ""
show = Show(LIBRARY_PATH, SHOW_NAME)
if not show.seasons() == show.containers:
    print(test_name, FAIL)

test_name = "Season.season_number"
print(test_name) if debug else ""
season = Season(LIBRARY_PATH, SHOW_NAME, SEASON_NUMBER)
if not season.season_number() == SEASON_NUMBER:
    print(test_name, FAIL)

test_name = "Season.seasons"
print(test_name) if debug else ""
season = Season(LIBRARY_PATH, SHOW_NAME, SEASON_NUMBER)
if season.seasons() is not None or season.seasons() == season.containers:
    print(test_name, FAIL)

test_name = "Season.extras"
print(test_name) if debug else ""
season = Season(LIBRARY_PATH, SHOW_NAME, SEASON_NUMBER)
if not season.extras() == season.containers:
    print(test_name, FAIL)

test_name = "Season.episodes"
print(test_name) if debug else ""
season = Season(LIBRARY_PATH, SHOW_NAME, SEASON_NUMBER)
if not season.episodes() == season.media:
    print(test_name, FAIL)

test_name = "extra.extras"
print(test_name) if debug else ""
extra = Extra(LIBRARY_PATH, SHOW_NAME, SEASON_NUMBER)
if extra.extras() is not None or extra.extras() == extra.containers:
    print(test_name, FAIL)

test_name = "id"

print(test_name) if debug else ""
mediaLibrary = MediaLibrary(LIBRARY_PATH)
if Container.id(mediaLibrary.path()) != mediaLibrary.id():
    print(test_name, FAIL)

show = Show(LIBRARY_PATH, SHOW_NAME)
if Container.id(show.show_name()) != show.id():
    print(test_name, FAIL)

season = Season(LIBRARY_PATH, SHOW_NAME, SEASON_NUMBER)
if (
    Container.id("{}{}{}".format(
        season.show_name(), "season", season.season_number()
    )) != season.id()
):
    print(test_name, FAIL)

extra = Extra(LIBRARY_PATH, SHOW_NAME, SEASON_NUMBER)
if (
    Container.id("{}{}{}{}".format(
        extra.show_name(), "season", extra.season_number(), "extra"
    )) != extra.id()
):
    print(test_name, FAIL)


print("container-tests: Successfully Completed")
