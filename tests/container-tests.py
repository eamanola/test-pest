import sys
import os
sys.path.append(os.path.join(sys.path[0], '..'))
from classes.container import Container, Show, Season, Extra
from classes.media import Media

debug = False;
debug = True;

RANDOM_NAME = "foo"
RANDOM_NAME2 = "bar"
FAIL = "FAIL";
PASS = "PASS";

test_name = "isheritance:"
print(test_name) if debug else "";

test_name = "Container()"
print(test_name) if debug else "";

container = Container(RANDOM_NAME);
if not isinstance(container, Container) or isinstance(container, Show) or isinstance(container, Season) or isinstance(container, Extra):
    print(test_name, FAIL);

test_name = "Show()"
print(test_name) if debug else "";

show = Show(RANDOM_NAME);
if not isinstance(show, (Container, Show)) or isinstance(container, Season) or isinstance(container, Extra):
    print(test_name, FAIL);

test_name = "Season()"
print(test_name) if debug else "";

season = Season(RANDOM_NAME);
if not isinstance(season, (Container, Show, Season)) or isinstance(container, Extra):
    print(test_name, FAIL);

test_name = "Extra()"
print(test_name) if debug else "";

extra = Extra(RANDOM_NAME);
if not isinstance(extra, (Container, Show, Season, Extra)):
    print(test_name, FAIL);

test_name = "Container.get_container"
print(test_name) if debug else "";

container = Container(RANDOM_NAME);

if not container.get_container(RANDOM_NAME2) == None:
    print(test_name, FAIL);

container2 = Container(RANDOM_NAME2);
container.containers.append(container2);

if not container.get_container(RANDOM_NAME2) == container2:
    print(test_name, FAIL);

if not container.get_container(RANDOM_NAME) == None:
    print(test_name, FAIL);

test_name = "Container.get_media"
print(test_name) if debug else "";
container = Container(RANDOM_NAME);

if not container.get_container(RANDOM_NAME2) == None:
    print(test_name, FAIL, 1);

media = Media(RANDOM_NAME2);
container.media.append(media);

if not container.get_media(RANDOM_NAME2) == media:
    print(test_name, FAIL, 2);

if not container.get_media(RANDOM_NAME) == None:
    print(test_name, FAIL, 3);

test_name = "Show.show_name"
print(test_name) if debug else "";
show = Show(RANDOM_NAME);
if not show.show_name() == RANDOM_NAME or not show.show_name() == show.container_name:
    print(test_name, FAIL);

test_name = "Show.seasons"
print(test_name) if debug else "";
show = Show(RANDOM_NAME);
if not show.seasons() == show.containers:
    print(test_name, FAIL);

test_name = "Season.seasons"
print(test_name) if debug else "";
season = Season(RANDOM_NAME);
if not season.seasons() == None or season.seasons() == season.containers:
    print(test_name, FAIL);

test_name = "Season.season_name"
print(test_name) if debug else "";
season = Season(RANDOM_NAME);
if not season.season_name() == RANDOM_NAME or not season.season_name() == season.container_name:
    print(test_name, FAIL);

test_name = "Season.extras"
print(test_name) if debug else "";
season = Season(RANDOM_NAME);
if not season.extras() == season.containers:
    print(test_name, FAIL);

test_name = "Season.episodes"
print(test_name) if debug else "";
season = Season(RANDOM_NAME);
if not season.episodes() == season.media:
    print(test_name, FAIL);

test_name = "extra.extras"
print(test_name) if debug else "";
extra = Extra(RANDOM_NAME);
if not extra.extras() == None or extra.extras() == extra.containers:
    print(test_name, FAIL);

print("Successfully Completed");
