import unittest
from classes.media import Media, Episode, Movie


class TestMedia(unittest.TestCase):

    def test_media(self):
        import hashlib

        media = Media("filepath", "played", parent="parent")
        self.assertEqual(media.file_path(), "filepath")
        self.assertEqual(media.subtitles, [])
        self.assertEqual(
            media.id(),
            hashlib.md5(media.file_path().encode('utf-8')).hexdigest()
        )
        self.assertEqual(media.played(), "played")
        self.assertEqual(media.parent(), "parent")

        media.set_parent("foobar")
        self.assertEqual(media.parent(), "foobar")

        media.set_played("foobar")
        self.assertEqual(media.played(), "foobar")

        self.assertRaises(NotImplementedError, media.title)
        self.assertRaises(NotImplementedError, media.thumbnail)

    def test_episode(self):
        episode = Episode(
            "file_path",
            "episode_number",
            "played",
            parent="parent",
            is_oad="is_oad",
            is_ncop="is_ncop",
            is_nced="is_nced",
            is_ova="is_ova")

        self.assertEqual(episode.episode_number(), "episode_number")
        self.assertEqual(episode.is_oad(), "is_oad")
        self.assertEqual(episode.is_ncop(), "is_ncop")
        self.assertEqual(episode.is_nced(), "is_nced")
        self.assertEqual(episode.is_ova(), "is_ova")
        self.assertIsInstance(episode, Media)

    def test_episode_is_extra(self):
        from classes.container import Container, Extra

        episode = Episode("file_path", "episode_number", "played")
        self.assertFalse(episode.is_extra())

        episode.set_parent(Container())
        self.assertFalse(episode.is_extra())

        episode.set_parent(Extra('library_path', 'show_name', 'season_number'))
        self.assertTrue(episode.is_extra())

        episode = Episode("file_path", "episode_number", "played", is_oad=True)
        self.assertTrue(episode.is_extra())

        episode = Episode("file_path", "episode_num", "played", is_ncop=True)
        self.assertTrue(episode.is_extra())

        episode = Episode("file_path", "episode_num", "played", is_nced=True)
        self.assertTrue(episode.is_extra())

        episode = Episode("file_path", "episode_number", "played", is_ova=True)
        self.assertTrue(episode.is_extra())

    def test_episode_is_extra(self):
        from classes.container import Extra

        episode = Episode("file_path", 1, "played")
        self.assertTrue(episode.title().startswith("Episode"))

        episode = Episode("file_path", 1, "played", is_oad=True)
        self.assertTrue(episode.title().startswith("OAD"))

        episode = Episode("file_path", 1, "played", is_ncop=True)
        self.assertTrue(episode.title().startswith("NCOP"))

        episode = Episode("file_path", 1, "played", is_nced=True)
        self.assertTrue(episode.title().startswith("NCED"))

        episode = Episode("file_path", 1, "played", is_ova=True)
        self.assertTrue(episode.title().startswith("OVA"))

        episode = Episode(
            "file_path", 1, "played", parent=Extra(
                'library_path', 'show_name', 'season_number'
            )
        )
        self.assertTrue(episode.title().startswith("Extra"))

    def test_episode_thumbnail(self):
        from classes.container import Extra, Season, Show, MediaLibrary
        import re

        mediaLibrary = MediaLibrary("path")
        show = Show('library_path', 'show_name', parent=mediaLibrary)
        season = Season('library_path', 'show_name', 1, parent=show)
        extra = Extra('library_path', 'show_name', 1, parent=season)
        episode = Episode("file_path", 1, "played", parent=extra)

        thumbnail = f"""
            {show.title()} {season.title()} {extra.title()} {episode.title()}
            """.strip()
        thumbnail = re.sub(r'[^A-Za-z0-9]', '.', thumbnail)
        thumbnail = re.sub(r'\.+', '.', thumbnail)

        self.assertEqual(episode.thumbnail(), thumbnail)

    def test_movie(self):
        from classes.identifiable import Identifiable
        movie = Movie("file_path", "title of movie", "played")
        self.assertIsInstance(movie, Media)
        self.assertIsInstance(movie, Identifiable)

        self.assertEqual(movie.title(), "title of movie")

        self.assertIsNone(movie.year())
        thumbnail = movie.title()
        self.assertEqual(movie.thumbnail(), thumbnail.replace(" ", "."))

        movie.set_year(2000)
        self.assertIsNotNone(movie.year())
        thumbnail = f"{movie.title()} ({movie.year()})"
        self.assertEqual(movie.thumbnail(), thumbnail.replace(" ", "."))


if __name__ == '__main__':
    unittest.main()
