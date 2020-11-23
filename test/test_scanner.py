import unittest
from mediafinder.scanner import Scanner


def test_file_paths():
    import sys
    import os

    test_folder_path = sys.path[0]

    if __name__ != '__main__':
        test_folder_path = os.sep.join([test_folder_path, 'test'])

    tmp = os.path.join(test_folder_path, 'tmp')

    test_files = [
        os.path.join(tmp, "movie.mkv"),
        os.path.join(tmp, "random.txt"),
        os.path.join(tmp, "Show 1", "episode 1.mkv"),
        os.path.join(tmp, "Show 1", "S01E2.mkv"),
        os.path.join(tmp, "Show 1", "S02E2.mkv"),
        os.path.join(tmp, "Show 1 (2007)", "S02E2.mkv"),
        os.path.join(tmp, "Show 2", "Season1", "some file 1.mkv"),
        os.path.join(tmp, "Show 2", "Season1", "some file 2.mkv"),
        os.path.join(
            tmp,
            "Show 2",
            "Season 2",
            "extra",
            "other file 1.mkv"
        )
    ]

    return tmp, test_files


def create_test_files(test, file_paths):
    from pathlib import Path
    import os

    for file_path in file_paths:
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        test.assertTrue(os.path.dirname(file_path))

        path.touch(exist_ok=True)
        test.assertTrue(os.path.exists(file_path))


def remove_test_files(test, base_path, file_paths):
    import shutil
    import os

    shutil.rmtree(base_path)
    for file_path in file_paths:
        test.assertFalse(os.path.exists(file_path))


class TestScanner(unittest.TestCase):

    def test_ls_path(self):
        base_path, file_paths = test_file_paths()
        create_test_files(self, file_paths)

        paths = Scanner.ls_path(base_path)
        for file_path in file_paths:
            self.assertTrue(file_path.replace(base_path, "") in paths)

        remove_test_files(self, base_path, file_paths)

    def test_filter_types(self):
        from mediafinder.file_name_parser import File_name_parser

        base_path, file_paths = test_file_paths()

        filtered_paths = Scanner.filter_types(file_paths)
        self.assertEqual(len(file_paths) - 1, len(filtered_paths))

        for filtered_path in filtered_paths:
            self.assertTrue(
                filtered_path.endswith(File_name_parser.FILE_EXTENSIONS)
            )

    def test_filter_media_library(self):
        from models.containers import MediaLibrary

        base_path, file_paths = test_file_paths()
        create_test_files(self, file_paths)

        filtered_paths = Scanner.filter_media_library(
            MediaLibrary(base_path)
        )
        self.assertEqual(len(file_paths) - 1, len(filtered_paths))

        remove_test_files(self, base_path, file_paths)

    def test_filter_show(self):
        from models.containers import Show

        base_path, file_paths = test_file_paths()
        create_test_files(self, file_paths)

        show = Show(base_path, "Show 1")

        filtered_paths = Scanner.filter_show(show)

        self.assertEqual(3, len(filtered_paths))

        for filtered_path in filtered_paths:
            self.assertTrue(show.show_name() in filtered_path)

        remove_test_files(self, base_path, file_paths)

    def test_filter_season(self):
        from models.containers import Season

        base_path, file_paths = test_file_paths()
        create_test_files(self, file_paths)

        season = Season(base_path, "Show 1", 2)

        filtered_paths = Scanner.filter_season(season)

        self.assertEqual(1, len(filtered_paths))

        for filtered_path in filtered_paths:
            self.assertTrue(season.show_name() in filtered_path)

        remove_test_files(self, base_path, file_paths)

    def test_filter_extra(self):
        from models.containers import Extra

        base_path, file_paths = test_file_paths()
        create_test_files(self, file_paths)

        extra = Extra(base_path, "Show 2", 2)

        filtered_paths = Scanner.filter_extra(extra)

        self.assertEqual(1, len(filtered_paths))

        for filtered_path in filtered_paths:
            self.assertTrue(extra.show_name() in filtered_path)

        remove_test_files(self, base_path, file_paths)

    def test_scan_media_library(self):
        from models.containers import MediaLibrary

        base_path, file_paths = test_file_paths()
        create_test_files(self, file_paths)

        container = Scanner.scan_media_library(MediaLibrary(base_path))
        self.assertEqual(len(container.containers), 3)
        self.assertEqual(len(container.media), 1)

        remove_test_files(self, base_path, file_paths)

    def test_scan_show(self):
        from models.containers import Show

        base_path, file_paths = test_file_paths()
        create_test_files(self, file_paths)

        container = Scanner.scan_show(Show(base_path, "Show 1"))
        self.assertEqual(len(container.containers), 2)
        self.assertEqual(len(container.media), 1)

        remove_test_files(self, base_path, file_paths)

    def test_scan_season(self):
        from models.containers import Season

        base_path, file_paths = test_file_paths()
        create_test_files(self, file_paths)

        container = Scanner.scan_season(Season(base_path, "Show 1", 1))
        self.assertEqual(len(container.containers), 0)
        self.assertEqual(len(container.media), 1)

        remove_test_files(self, base_path, file_paths)

    def test_scan_extra(self):
        from models.containers import Extra

        base_path, file_paths = test_file_paths()
        create_test_files(self, file_paths)

        container = Scanner.scan_extra(Extra(base_path, "Show 2", 1))
        self.assertIsNone(container)

        container = Scanner.scan_show(Extra(base_path, "Show 2", 2))
        self.assertEqual(len(container.containers), 0)
        self.assertEqual(len(container.media), 1)

        remove_test_files(self, base_path, file_paths)


if __name__ == '__main__':
    unittest.main()
