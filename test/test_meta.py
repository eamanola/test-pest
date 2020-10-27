import unittest
from classes.meta import Meta, Episode_Meta


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
        from classes.media import Episode
        episodes = [
            Episode_Meta(1, "title", "summary"),
            Episode_Meta(2, "title", "summary"),
            Episode_Meta(3, "title", "summary")
        ]

        meta = Meta("id", "title", "rating", "image_name", episodes, "desc")

        episode1 = Episode("file_path", 1, "played")
        episode2 = Episode("file_path", 2, "played")
        episode3 = Episode("file_path", 3, "played")
        episode4 = Episode("file_path", 4, "played")

        self.assertEqual(episodes[0], meta.get_episode(episode1))
        self.assertEqual(episodes[1], meta.get_episode(episode2))
        self.assertEqual(episodes[2], meta.get_episode(episode3))
        self.assertIsNone(meta.get_episode(episode4))

    def test_episode_meta(self):
        episode_meta = Episode_Meta("episode_number", "title", "summary")

        self.assertEqual(episode_meta.episode_number(), "episode_number")
        self.assertEqual(episode_meta.title(), "title")
        self.assertEqual(episode_meta.summary(), "summary")


if __name__ == '__main__':
    unittest.main()
