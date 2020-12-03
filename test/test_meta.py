import unittest
from models.meta import Meta, Episode_Meta


class TestMeta(unittest.TestCase):

    def test_meta(self):
        meta = Meta(
            "id",
            "title",
            "rating",
            "image_name",
            "episodes",
            "description"
        )

        self.assertEqual(meta.id(), "id")
        self.assertEqual(meta.title(), "title")
        self.assertEqual(meta.rating(), "rating")
        self.assertEqual(meta.image_name(), "image_name")
        self.assertEqual(meta.episodes(), "episodes")
        self.assertEqual(meta.description(), "description")

    def test_get_episode(self):
        from models.media import Episode
        from models.media import Season, Show
        episodes = [
            Episode_Meta(1, -1, "title", "summary"),
            Episode_Meta(2, 0, "title", "summary"),
            Episode_Meta(3, 0, "title", "summary"),
            Episode_Meta(4, 1, "title", "summary")
        ]

        meta = Meta("id", "title", "rating", "image_name", episodes, "desc")

        season1 = Season("library_path", "show_name", 1)
        season2 = Season("library_path", "show_name", 2)
        show1 = Show("library_path", "show_name")

        episode1 = Episode("file_path", 1, "played")
        episode2 = Episode("file_path", 2, "played")
        episode3 = Episode("file_path", 3, "played")
        episode4 = Episode("file_path", 4, "played")
        episode41 = Episode("file_path", 4, "played", parent=season1)
        episode42 = Episode("file_path", 4, "played", parent=season2)
        episode43 = Episode("file_path", 4, "played", parent=show1)
        episode5 = Episode("file_path", 5, "played")

        self.assertEqual(episodes[0], meta.get_episode(episode1))
        self.assertEqual(episodes[1], meta.get_episode(episode2))
        self.assertEqual(episodes[2], meta.get_episode(episode3))
        self.assertIsNone(meta.get_episode(episode4))
        self.assertEqual(episodes[3], meta.get_episode(episode41))
        self.assertIsNone(meta.get_episode(episode42))
        self.assertIsNone(meta.get_episode(episode43))
        self.assertIsNone(meta.get_episode(episode5))

    def test_episode_meta(self):
        episode_meta = Episode_Meta(
            "episode_number", "season_number", "title", "summary"
        )

        self.assertEqual(episode_meta.episode_number(), "episode_number")
        self.assertEqual(episode_meta.season_number(), "season_number")
        self.assertEqual(episode_meta.title(), "title")
        self.assertEqual(episode_meta.summary(), "summary")


if __name__ == '__main__':
    unittest.main()
