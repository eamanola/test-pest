import unittest
import test.testutils as testutils
from classes.container import Container, MediaLibrary, Show, Season, Extra
from classes.media import Media


class TestContainer(unittest.TestCase):

    def test_init(self):
        container = Container()

        self.assertIsInstance(container, Container)
        self.assertNotIsInstance(container, MediaLibrary)
        self.assertNotIsInstance(container, Show)
        self.assertNotIsInstance(container, Season)
        self.assertNotIsInstance(container, Extra)

        container = Container()
        self.assertIsNone(container.parent())

        parent = Container()
        container = Container(parent=parent)
        self.assertTrue(testutils.compare_containers(
            container.parent(), parent
        ))

        container = Show("path", "showname")

        self.assertIsInstance(container, Container)
        self.assertIsInstance(container, MediaLibrary)
        self.assertIsInstance(container, Show)
        self.assertNotIsInstance(container, Season)
        self.assertNotIsInstance(container, Extra)

        container = Season("path", "showname", 1)

        self.assertIsInstance(container, Container)
        self.assertIsInstance(container, MediaLibrary)
        self.assertIsInstance(container, Show)
        self.assertIsInstance(container, Season)
        self.assertNotIsInstance(container, Extra)

        container = Extra("path", "showname", 1)

        self.assertIsInstance(container, Container)
        self.assertIsInstance(container, MediaLibrary)
        self.assertIsInstance(container, Show)
        self.assertIsInstance(container, Season)
        self.assertIsInstance(container, Extra)

    def test_parent(self):
        container = Container()
        self.assertIsNone(container.parent())

        parent = Container()
        container = Container(parent=parent)
        self.assertTrue(testutils.compare_containers(
            container.parent(), parent
        ))

        container.set_parent(None)
        self.assertIsNone(container.parent())

    def test_get_container(self):
        container = Container()
        show1 = Show("path", "showname")
        show2 = Show("path", "showname2")
        container.containers.append(show1)
        show1.containers.append(show2)

        self.assertTrue(testutils.compare_containers(
            show1,
            container.get_container(show1.id())
        ))

        self.assertIsNone(container.get_container(show2.id()))
        self.assertIsNone(container.get_container("foobar"))

    def test_find_container(self):
        container = Container()
        show1 = Show("path", "showname")
        show2 = Show("path", "showname2")
        container.containers.append(show1)
        show1.containers.append(show2)

        self.assertTrue(testutils.compare_containers(
            show1,
            container.find_container(show1.id())
        ))

        self.assertTrue(testutils.compare_containers(
            container.find_container(show2.id()),
            show2
        ))
        self.assertIsNone(container.find_container("foobar"))

    def test_get_media(self):
        container = Container()

        media1 = Media("file_path", False)
        container.media.append(media1)

        show1 = Show("path", "showname")
        media2 = Media("file_path2", False)
        container.containers.append(show1)
        show1.media.append(media2)

        self.assertTrue(testutils.compare_media(
            media1,
            container.get_media(media1.id())
        ))

        self.assertIsNone(container.get_media(media2.id()))
        self.assertIsNone(container.get_media("foobar"))

    def test_hashid(self):
        import hashlib
        RANDOM_STR = "foobar"
        self.assertEqual(
            hashlib.md5(RANDOM_STR.encode('utf-8')).hexdigest(),
            Container().hash_id(RANDOM_STR)
        )

    def test_id(self):
        self.assertRaises(NotImplementedError, Container().id)

    def test_title(self):
        self.assertRaises(NotImplementedError, Container().title)

    def test_unplayed_count(self):
        container = Container()
        self.assertEqual(container.unplayed_count(), 0)

        RANDOM_INT = 22
        container.set_unplayed_count(RANDOM_INT)
        self.assertEqual(container.unplayed_count(), RANDOM_INT)


class TestMediaLibrary(unittest.TestCase):
    def test_init(self):
        mediaLibrary = MediaLibrary("path")

        self.assertIsInstance(mediaLibrary, Container)
        self.assertIsInstance(mediaLibrary, MediaLibrary)
        self.assertNotIsInstance(mediaLibrary, Show)
        self.assertNotIsInstance(mediaLibrary, Season)
        self.assertNotIsInstance(mediaLibrary, Extra)

        mediaLibrary = MediaLibrary("path")
        self.assertIsNone(mediaLibrary.parent())

        parent = Container()
        mediaLibrary = MediaLibrary("path", parent=parent)
        self.assertTrue(testutils.compare_containers(
            mediaLibrary.parent(),
            parent
        ))

    def test_id(self):
        mediaLibrary = MediaLibrary("path")
        self.assertEqual(
            mediaLibrary.id(),
            mediaLibrary.hash_id(mediaLibrary.path())
        )

    def test_title(self):
        mediaLibrary = MediaLibrary("path")
        self.assertEqual(
            mediaLibrary.title(),
            mediaLibrary.path()
        )

    def test_path(self):
        PATH = "path"
        mediaLibrary = MediaLibrary(PATH)
        self.assertEqual(
            mediaLibrary.path(),
            PATH
        )


class TestShow(unittest.TestCase):
    def test_init(self):
        show = Show("path", "showname")

        self.assertIsInstance(show, Container)
        self.assertIsInstance(show, MediaLibrary)
        self.assertIsInstance(show, Show)
        self.assertNotIsInstance(show, Season)
        self.assertNotIsInstance(show, Extra)

        show = Show("path", "showname")
        self.assertIsNone(show.parent())

        parent = Container()
        show = Show("path", "showname", parent=parent)
        self.assertTrue(testutils.compare_containers(
            show.parent(),
            parent
        ))

        PATH = "path"
        show = Show(PATH, "showname")
        self.assertEqual(PATH, show.path())

    def test_id(self):
        show = Show("path", "showname")
        self.assertEqual(
            show.id(),
            show.hash_id(show.show_name())
        )

    def test_title(self):
        show = Show("path", "showname")
        self.assertEqual(
            show.title(),
            show.show_name()
        )

    def test_show_name(self):
        SHOW_NAME = "showname"
        show = Show("path", SHOW_NAME)
        self.assertEqual(
            show.show_name(),
            SHOW_NAME
        )


class TestSeason(unittest.TestCase):
    def test_init(self):
        season = Season("path", "showname", 1)

        self.assertIsInstance(season, Container)
        self.assertIsInstance(season, MediaLibrary)
        self.assertIsInstance(season, Show)
        self.assertIsInstance(season, Season)
        self.assertNotIsInstance(season, Extra)

        season = Season("path", "showname", 1)
        self.assertIsNone(season.parent())

        parent = Container()
        season = Season("path", "showname", 1, parent=parent)
        self.assertTrue(testutils.compare_containers(
            season.parent(),
            parent
        ))

        PATH = "path"
        season = Season(PATH, "showname", 1)
        self.assertEqual(PATH, season.path())

        SHOW_NAME = "showname"
        season = Season("path", SHOW_NAME, 1)
        self.assertEqual(
            season.show_name(),
            SHOW_NAME
        )

    def test_id(self):
        season = Season("path", "showname", 1)
        id_str = "{}{}{}".format(
            season.show_name(),
            "season",
            season.season_number()
        )
        self.assertEqual(
            season.id(),
            season.hash_id(id_str)
        )

    def test_title(self):
        season = Season("path", "showname", 1)
        self.assertEqual(
            season.title(),
            "Season {:02d}".format(season.season_number())
        )

    def test_season_number(self):
        SEASON_NUMBER = 22
        season = Season("path", "showname", SEASON_NUMBER)
        self.assertEqual(season.season_number(), SEASON_NUMBER)


class TestExtra(unittest.TestCase):
    def test_init(self):
        extra = Extra("path", "showname", 1)

        self.assertIsInstance(extra, Container)
        self.assertIsInstance(extra, MediaLibrary)
        self.assertIsInstance(extra, Show)
        self.assertIsInstance(extra, Season)
        self.assertIsInstance(extra, Extra)

        extra = Extra("path", "showname", 1)
        self.assertIsNone(extra.parent())

        parent = Container()
        extra = Extra("path", "showname", 1, parent=parent)
        self.assertTrue(testutils.compare_containers(
            extra.parent(),
            parent
        ))

        PATH = "path"
        extra = Extra(PATH, "showname", 1)
        season = Season(PATH, "showname", 1)
        self.assertEqual(PATH, season.path())

        SHOW_NAME = "showname"
        extra = Extra("path", SHOW_NAME, 1)
        self.assertEqual(
            extra.show_name(),
            SHOW_NAME
        )

        SEASON_NUMBER = 22
        extra = Extra("path", "showname", SEASON_NUMBER)
        self.assertEqual(extra.season_number(), SEASON_NUMBER)

    def test_id(self):
        extra = Extra("path", "showname", 1)
        id_str = "{}{}{}{}".format(
            extra.show_name(),
            "season",
            extra.season_number(),
            "extra"
        )
        self.assertEqual(
            extra.id(),
            extra.hash_id(id_str)
        )

    def test_title(self):
        extra = Extra("path", "showname", 1)
        self.assertEqual(
            extra.title(),
            "Extra"
        )


if __name__ == '__main__':
    unittest.main()
