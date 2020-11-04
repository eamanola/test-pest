import unittest
from classes.images import Images


class TestImages(unittest.TestCase):

    def test_images(self):
        self.assertEqual(Images.THUMBNAIL_FOLDER, ['images', 'thumbnails'])
        self.assertEqual(Images.POSTER_FOLDER, ['images', 'posters'])

    def test_thumbnails(self):
        import sys
        import os
        from classes.media import Episode
        from classes.container import MediaLibrary

        media = Episode(
            "foobar",
            episode_number=1,
            played=False)
        self.assertEqual(
            Images.thumbnail(media),
            f'{"/".join(Images.THUMBNAIL_FOLDER)}/{media.thumbnail()}.png'
        )

        SYS_PATH_0 = sys.path[0]
        self.assertEqual(SYS_PATH_0, sys.path[0])

        if __name__ != '__main__':
            sys.path[0] = os.sep.join([sys.path[0], 'test'])

        self.assertTrue(os.path.exists(sys.path[0]))
        parent = MediaLibrary(sys.path[0])

        # long clip
        long_clip = 'sample-video-5min.mkv'
        self.assertTrue(os.path.exists(os.path.join(
            sys.path[0],
            long_clip
        )))
        media = Episode(
            long_clip,
            episode_number=1,
            played=False,
            parent=parent)

        thumbnail_path = os.path.join(
            sys.path[0],
            os.sep.join(Images.THUMBNAIL_FOLDER),
            f"{media.thumbnail()}.png"
        )
        self.assertFalse(os.path.exists(thumbnail_path))

        thumbnail = Images.thumbnail(media, create_ifmissing=True)
        self.assertTrue(os.path.exists(thumbnail_path))

        os.remove(thumbnail_path)
        self.assertFalse(os.path.exists(thumbnail_path))
        os.removedirs(os.path.dirname(thumbnail_path))
        self.assertFalse(os.path.exists(os.path.dirname(thumbnail_path)))

        # short clip
        short_clip = 'sample-video-12s.mkv'
        self.assertTrue(os.path.exists(os.path.join(
            sys.path[0],
            short_clip
        )))
        media = Episode(
            short_clip,
            episode_number=2,
            played=False,
            parent=parent)

        thumbnail_path = os.path.join(
            sys.path[0],
            os.sep.join(Images.THUMBNAIL_FOLDER),
            f"{media.thumbnail()}.png"
        )
        self.assertFalse(os.path.exists(thumbnail_path))

        thumbnail = Images.thumbnail(media, create_ifmissing=True)
        self.assertTrue(os.path.exists(thumbnail_path))

        os.remove(thumbnail_path)
        self.assertFalse(os.path.exists(thumbnail_path))
        os.removedirs(os.path.dirname(thumbnail_path))
        self.assertFalse(os.path.exists(os.path.dirname(thumbnail_path)))

        # parentless clip
        no_parent_clip = 'sample-video-12s.mkv'
        self.assertTrue(os.path.exists(os.path.join(
            sys.path[0],
            no_parent_clip
        )))
        media = Episode(
            no_parent_clip,
            episode_number=3,
            played=False,
            parent=None)

        thumbnail_path = os.path.join(
            sys.path[0],
            os.sep.join(Images.THUMBNAIL_FOLDER),
            f"{media.thumbnail()}.png"
        )
        self.assertFalse(os.path.exists(thumbnail_path))

        thumbnail = Images.thumbnail(media, create_ifmissing=True)
        self.assertFalse(os.path.exists(thumbnail_path))

        # missing clip
        missing_clip = 'foobar'
        self.assertFalse(os.path.exists(os.path.join(
            sys.path[0],
            missing_clip
        )))
        media = Episode(
            missing_clip,
            episode_number=3,
            played=False,
            parent=None)

        thumbnail_path = os.path.join(
            sys.path[0],
            os.sep.join(Images.THUMBNAIL_FOLDER),
            f"{media.thumbnail()}.png"
        )
        self.assertFalse(os.path.exists(thumbnail_path))

        thumbnail = Images.thumbnail(media, create_ifmissing=True)
        self.assertFalse(os.path.exists(thumbnail_path))

        if __name__ != '__main__':
            sys.path[0] = os.sep.join(sys.path[0].split(os.sep)[0:-1])

        self.assertEqual(SYS_PATH_0, sys.path[0])

    def test_poster(self):
        from classes.media import Movie
        from classes.meta import Meta

        media = Movie("foo", "bar", played=False)
        self.assertIsNone(Images.poster(media))

        media.set_meta(Meta(
            "id",
            "title",
            "rating",
            "image_name",
            "episodes",
            "description"
        ))
        self.assertEqual(
            Images.poster(media),
            f'{"/".join(Images.POSTER_FOLDER)}/{media.meta().image_name()}'
        )


if __name__ == '__main__':
    unittest.main()
