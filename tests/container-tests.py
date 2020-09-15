import sys
import os
sys.path.append(os.path.join(sys.path[0], '..'))
from classes.container import Container, Show, Season, Extra
from classes.media import Media

debug = True;
debug = False;

RANDOM_STR = "foo"
RANDOM_STR2 = "bar"
RANDOM_INT = 22;
FAIL = "FAIL";
PASS = "PASS";

test_name = "isheritance:"
print(test_name) if debug else "";

test_name = "Container()"
print(test_name) if debug else "";

container = Container(RANDOM_STR);
if not isinstance(container, Container) or isinstance(container, Show) or isinstance(container, Season) or isinstance(container, Extra):
    print(test_name, FAIL);

test_name = "Show()"
print(test_name) if debug else "";

show = Show(RANDOM_STR);
if not isinstance(show, (Container, Show)) or isinstance(container, Season) or isinstance(container, Extra):
    print(test_name, FAIL);

test_name = "Season()"
print(test_name) if debug else "";

season = Season(RANDOM_STR, RANDOM_INT);
if not isinstance(season, (Container, Show, Season)) or isinstance(container, Extra):
    print(test_name, FAIL);

test_name = "Extra()"
print(test_name) if debug else "";

extra = Extra(RANDOM_STR);
if not isinstance(extra, (Container, Show, Season, Extra)):
    print(test_name, FAIL);

test_name = "Container.get_container"
print(test_name) if debug else "";

container = Container(RANDOM_STR);

if not container.get_container(RANDOM_STR2) == None:
    print(test_name, FAIL);

container2 = Container(RANDOM_STR2);
container.containers.append(container2);

if not container.get_container(RANDOM_STR2) == container2:
    print(test_name, FAIL);

if not container.get_container(RANDOM_STR) == None:
    print(test_name, FAIL);

test_name = "Container.get_media"
print(test_name) if debug else "";
container = Container(RANDOM_STR);

if not container.get_container(RANDOM_STR2) == None:
    print(test_name, FAIL, 1);

media = Media(RANDOM_STR2);
container.media.append(media);

if not container.get_media(RANDOM_STR2) == media:
    print(test_name, FAIL, 2);

if not container.get_media(RANDOM_STR) == None:
    print(test_name, FAIL, 3);

test_name = "Show.show_name"
print(test_name) if debug else "";
show = Show(RANDOM_STR);
if not show.show_name() == RANDOM_STR or not show.show_name() == show.container_name:
    print(test_name, FAIL);

test_name = "Show.seasons"
print(test_name) if debug else "";
show = Show(RANDOM_STR);
if not show.seasons() == show.containers:
    print(test_name, FAIL);

test_name = "Show.year"
print(test_name) if debug else "";
show = Show(RANDOM_STR);
if not show.year == None:
    print(test_name, FAIL);
show.year = RANDOM_INT;
if not show.year == RANDOM_INT:
    print(test_name, FAIL);

test_name = "Season.season_number"
print(test_name) if debug else "";
season = Season(RANDOM_STR, RANDOM_INT);
if not season.season_number() == RANDOM_INT:
    print(test_name, FAIL);

test_name = "Season.seasons"
print(test_name) if debug else "";
season = Season(RANDOM_STR, RANDOM_INT);
if not season.seasons() == None or season.seasons() == season.containers:
    print(test_name, FAIL);

test_name = "Season.season_name"
print(test_name) if debug else "";
season = Season(RANDOM_STR, RANDOM_INT);
if not season.season_name() == RANDOM_STR or not season.season_name() == season.container_name:
    print(test_name, FAIL);

test_name = "Season.extras"
print(test_name) if debug else "";
season = Season(RANDOM_STR, RANDOM_INT);
if not season.extras() == season.containers:
    print(test_name, FAIL);

test_name = "Season.episodes"
print(test_name) if debug else "";
season = Season(RANDOM_STR, RANDOM_INT);
if not season.episodes() == season.media:
    print(test_name, FAIL);

test_name = "extra.extras"
print(test_name) if debug else "";
extra = Extra(RANDOM_STR);
if not extra.extras() == None or extra.extras() == extra.containers:
    print(test_name, FAIL);

print("container-tests: Successfully Completed");
