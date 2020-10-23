import sys
import os
from classes.file_name_parser import File_name_parser

import unittest
from classes.ext_title_to_id_file_parser import Ext_title_to_id_file_parser


class TestFile_name_parser(unittest.TestCase):
    def test_is_ova(self):
        term = "OVA"
        self.assertTrue(File_name_parser.is_ova(f"{term}as s/aa aa"))
        self.assertTrue(File_name_parser.is_ova(f"as s/{term}aa aa"))
        self.assertTrue(File_name_parser.is_ova(f"as s/aa aa{term}"))
        self.assertFalse(File_name_parser.is_ova(f"as s/{term.lower()}aa aa"))
        self.assertFalse(File_name_parser.is_ova(f"{term.lower()}as s/aa aa"))
        self.assertFalse(File_name_parser.is_ova(f"as s/aa aa{term.lower()}"))
        self.assertFalse(File_name_parser.is_ova(f"as s/aa aa"))

    def test_is_nced(self):
        term = "NCED"
        self.assertTrue(File_name_parser.is_nced(f"as s/{term}aa aa"))
        self.assertTrue(File_name_parser.is_nced(f"{term}as s/aa aa"))
        self.assertTrue(File_name_parser.is_nced(f"as s/aa aa{term}"))
        self.assertFalse(File_name_parser.is_nced(f"as s/{term.lower()}aa aa"))
        self.assertFalse(File_name_parser.is_nced(f"{term.lower()}as s/aa aa"))
        self.assertFalse(File_name_parser.is_nced(f"as sa/aa a{term.lower()}"))
        self.assertFalse(File_name_parser.is_nced(f"as s/aa aa"))

    def test_is_ncop(self):
        term = "NCOP"
        self.assertTrue(File_name_parser.is_ncop(f"as s/{term}aa aa"))
        self.assertTrue(File_name_parser.is_ncop(f"{term}as s/aa aa"))
        self.assertTrue(File_name_parser.is_ncop(f"as s/aa aa{term}"))
        self.assertFalse(File_name_parser.is_ncop(f"as s/{term.lower()}aa aa"))
        self.assertFalse(File_name_parser.is_ncop(f"{term.lower()}as s/aa aa"))
        self.assertFalse(File_name_parser.is_ncop(f"as s/aa aa{term.lower()}"))
        self.assertFalse(File_name_parser.is_ncop(f"as s/aa aa"))

    def test_is_oad(self):
        term = "OAD"
        self.assertTrue(File_name_parser.is_oad(f"as s/{term}aa aa"))
        self.assertTrue(File_name_parser.is_oad(f"{term}as s/aa aa"))
        self.assertTrue(File_name_parser.is_oad(f"as s/aa aa{term}"))
        self.assertFalse(File_name_parser.is_oad(f"as s/{term.lower()}aa aa"))
        self.assertFalse(File_name_parser.is_oad(f"{term.lower()}as s/aa aa"))
        self.assertFalse(File_name_parser.is_oad(f"as s/aa aa{term.lower()}"))
        self.assertFalse(File_name_parser.is_oad(f"as s/aa aa"))

    def test_is_ncop(self):
        term = "Extra"
        self.assertTrue(File_name_parser.is_extra(f"a s/{term}aa aa"))
        self.assertTrue(File_name_parser.is_extra(f"{term}a s/aa aa"))
        self.assertTrue(File_name_parser.is_extra(f"a s/aa aa{term}"))
        self.assertTrue(File_name_parser.is_extra(f"a s/{term.lower()}aa aa"))
        self.assertTrue(File_name_parser.is_extra(f"{term.lower()}as s/a aa"))
        self.assertTrue(File_name_parser.is_extra(f"a s/aa aa{term.lower()}"))
        self.assertFalse(File_name_parser.is_extra(f"a s/aa aa"))

        term = "NCOP"
        self.assertTrue(File_name_parser.is_extra(f"as s/{term}aa aa"))

        term = "NCED"
        self.assertTrue(File_name_parser.is_extra(f"as s/{term}aa aa"))

        term = "OVA"
        self.assertTrue(File_name_parser.is_extra(f"as s/{term}aa aa"))

        term = "OAD"
        self.assertTrue(File_name_parser.is_extra(f"as s/{term}aa aa"))

    def test_is_subtitle(self):
        for extension in File_name_parser.SUBTITLE_EXTENSIONS:
            self.assertTrue(File_name_parser.is_subtitle(
                f"path-to-file/filename{extension}"
            ))
            self.assertFalse(File_name_parser.is_subtitle(
                f"path-to-file/filename{extension}foo"
            ))

        self.assertFalse(File_name_parser.is_subtitle(
            f"path-to-file/filename"
        ))

    def test_is_media(self):
        for extension in File_name_parser.MEDIA_EXTENSIONS:
            self.assertTrue(File_name_parser.is_media(
                f"path-to-file/filename{extension}"
            ))
            self.assertFalse(File_name_parser.is_media(
                f"path-to-file/filename{extension}foo"
            ))

        self.assertFalse(File_name_parser.is_media(
            f"path-to-file/filename"
        ))

    def test_remove_file_extension(self):
        extension = ".ext"
        self.assertFalse(extension in File_name_parser.FILE_EXTENSIONS)
        self.assertEqual(
            File_name_parser.remove_file_extension(
                f"path-to-file/filename{extension}"
            ),
            f"path-to-file/filename{extension}"
        )

        for extension in File_name_parser.FILE_EXTENSIONS:
            self.assertEqual(
                File_name_parser.remove_file_extension(
                    f"path-to-file/filename{extension}"
                ),
                "path-to-file/filename"
            )
            self.assertEqual(
                File_name_parser.remove_file_extension(
                    f"path-to-file/funny.file.name{extension}"
                ),
                "path-to-file/funny.file.name"
            )

        for extension in File_name_parser.SUBTITLE_EXTENSIONS:
            for lang in File_name_parser.SUBTITLE_LANGS:
                self.assertEqual(
                    File_name_parser.remove_file_extension(
                        f"path-to-file/filename{lang}{extension}"
                    ),
                    "path-to-file/filename"
                )

        for extension in File_name_parser.MEDIA_EXTENSIONS:
            for lang in File_name_parser.SUBTITLE_LANGS:
                self.assertEqual(
                    File_name_parser.remove_file_extension(
                        f"path-to-file/filename{lang}{extension}"
                    ),
                    f"path-to-file/filename{lang}"
                )

    def test_remove_meta_tags(self):
        tag = "(foobar)"
        self.assertEqual(
            File_name_parser.remove_meta_tags(
                f"{tag}path-to-{tag}file/filename{tag}"
            ),
            f"path-to-file/filename"
        )
        self.assertEqual(
            File_name_parser.remove_meta_tags(
                f"{tag} path-to-{tag} file/filename{tag} "
            ),
            f"path-to-file/filename"
        )
        self.assertEqual(
            File_name_parser.remove_meta_tags(
                f" {tag}path-to- {tag}file/filename {tag}"
            ),
            f" path-to- file/filename "
        )

    def test_remove_user_tags(self):
        tag = "[foobar]"
        self.assertEqual(
            File_name_parser.remove_user_tags(
                f"{tag}path-to-{tag}file/filename{tag}"
            ),
            f"path-to-file/filename"
        )
        self.assertEqual(
            File_name_parser.remove_user_tags(
                f"{tag} path-to-{tag} file/filename{tag} "
            ),
            f"path-to-file/filename"
        )
        self.assertEqual(
            File_name_parser.remove_user_tags(
                f" {tag}path-to- {tag}file/filename {tag}"
            ),
            f" path-to- file/filename "
        )

    def test_remove_tags(self):
        tag = "[foo] (bar)"
        self.assertEqual(
            File_name_parser.remove_tags(
                f"{tag}path-to-{tag}file/filename{tag}"
            ),
            f"path-to-file/filename"
        )

    def test_guess_year(self):
        year = 2000
        for tag in (f"[{year}]", f"({year})", f" {year} ", f".{year}."):
            self.assertEqual(
                File_name_parser.guess_year(
                    f"{tag}path-to-file/filename"
                ),
                year
            )
            self.assertEqual(
                File_name_parser.guess_year(
                    f"path-to-{tag}file/filename"
                ),
                year
            )
            self.assertEqual(
                File_name_parser.guess_year(
                    f"path-to-file/filename{tag}"
                ),
                year
            )

        for tag in (f' {year}', f'.{year}'):
            self.assertEqual(
                File_name_parser.guess_year(
                    f"{tag}path-to-file/filename"
                ),
                File_name_parser.UNKNOWN_YEAR
            )
            self.assertEqual(
                File_name_parser.guess_year(
                    f"path-to-{tag}file/filename"
                ),
                File_name_parser.UNKNOWN_YEAR
            )
            self.assertEqual(
                File_name_parser.guess_year(
                    f"path-to-file/filename{tag}"
                ),
                year
            )

        for tag in (f'{year} ', f'{year}.'):
            self.assertEqual(
                File_name_parser.guess_year(
                    f"{tag}path-to-file/filename"
                ),
                year
            )
            self.assertEqual(
                File_name_parser.guess_year(
                    f"path-to-{tag}file/filename"
                ),
                File_name_parser.UNKNOWN_YEAR
            )
            self.assertEqual(
                File_name_parser.guess_year(
                    f"path-to-file/filename{tag}"
                ),
                File_name_parser.UNKNOWN_YEAR
            )

        for tag in (f'{year}', f'{year}'):
            self.assertEqual(
                File_name_parser.guess_year(
                    f"{tag}path-to-file/filename"
                ),
                File_name_parser.UNKNOWN_YEAR
            )
            self.assertEqual(
                File_name_parser.guess_year(
                    f"path-to-{tag}file/filename"
                ),
                File_name_parser.UNKNOWN_YEAR
            )
            self.assertEqual(
                File_name_parser.guess_year(
                    f"path-to-file/filename{tag}"
                ),
                File_name_parser.UNKNOWN_YEAR
            )

        self.assertEqual(
            File_name_parser.guess_year(
                f"path-to-file/filename(98)"
            ),
            File_name_parser.UNKNOWN_YEAR
        )

        self.assertEqual(
            File_name_parser.guess_year(
                f"path-to-file/filename"
            ),
            File_name_parser.UNKNOWN_YEAR
        )

    def test_guess_episode(self):
        ep_num = 1
        episode_info = [
            f"EPISODE{ep_num}", f"episode{ep_num}", f"Episode{ep_num}",
            f"E{ep_num}", f"e{ep_num}",
            f"EP{ep_num}", f"ep{ep_num}", f"Ep{ep_num}",

            f'extra{ep_num}', f'EXTRA{ep_num}', f'Extra{ep_num}',
            f'OAD{ep_num}',
            f'NCOP{ep_num}',
            f'NCED{ep_num}',
            f'OVA{ep_num}',
        ]

        for info in episode_info:
            for success in [
                f"path-to-file/filename {info}",
                f"path-to-file/file {info} name",
                f"path-to-file/{info} filename",
                f"path-to-file/filename S1{info}",
                f"path-to-file/file S1{info} name",
                f"path-to-file/S1{info} filename",
                f"path-to-file/filename.{info}",
                f"path-to-file/file.{info}.name",
                f"path-to-file/{info}.filename",
                f"path-to-file/{info}",
                f"path-to-file/{info}.mkv",
                f"path-to-file/S1{info}.mkv",
                f"path-to-file {info}/filename"
            ]:
                self.assertEqual(
                    File_name_parser.guess_episode(success),
                    ep_num
                )

            for fail in [
                f"path-to-file/filename{info}",
                f"path-to-file/file{info}name",
                f"path-to-file/{info}filename"
            ]:
                self.assertEqual(
                    File_name_parser.guess_episode(fail),
                    File_name_parser.UNKNOWN_EPISODE
                )

        for success in [
            f"path-to-file/filename {ep_num}",
            f"path-to-file/file {ep_num} name",
            f"path-to-file/{ep_num} filename",

            f"path-to-file/filename.{ep_num}",
            f"path-to-file/file.{ep_num}.name",
            f"path-to-file/{ep_num}.filename",
            f"path-to-file/{ep_num}",
            f"path-to-file/{ep_num}.mkv"
        ]:
            self.assertEqual(
                File_name_parser.guess_episode(success),
                ep_num
            )

        for fail in [
            f"path-to-file/filename S1{ep_num}",
            f"path-to-file/file S1{ep_num} name",
            f"path-to-file/S1{ep_num} filename",
            f"path-to-file/S1{ep_num}.mkv"
            f"path-to-file/filename{ep_num}",
            f"path-to-file/file{ep_num}name",
            f"path-to-file/{ep_num}filename",
            f"path-to-file {ep_num}/filename",
            f"filename S1{ep_num}"
        ]:
            self.assertEqual(
                File_name_parser.guess_episode(fail),
                File_name_parser.UNKNOWN_EPISODE
            )

    def test_guess_season(self):
        season_num = 1

        for success in [
            f'show/Season {season_num}/e1.mkv',
            f'show/Season{season_num}/e1.mkv',
            f'show/Season.{season_num}/e1.mkv',
            f'show/S {season_num}/e1.mkv',
            f'show/S{season_num}/e1.mkv',
            f'show/S.{season_num}/e1.mkv',
            f'show/S{season_num}E01.mkv'
        ]:
            self.assertEqual(
                File_name_parser.guess_episode(success),
                season_num
            )

    def test_shows(self):
        folder = "test" if __name__ != '__main__' else ""

        path = os.path.join(sys.path[0], folder, "test-shows")
        with open(path, "r") as test_shows:
            line = test_shows.readline()

            while line:
                if line.startswith('#') or not line.strip():
                    line = test_shows.readline()
                    continue
                elif line.strip() == "EOF":
                    break

                # new test block
                file_name = line.strip()

                line = test_shows.readline().strip()
                self.assertEqual(
                    File_name_parser.guess_show_name(file_name), line
                )
                line = test_shows.readline().strip()
                self.assertEqual(
                    File_name_parser.guess_season(file_name), int(line)
                )
                line = test_shows.readline().strip()
                self.assertEqual(
                    File_name_parser.guess_episode(file_name), int(line)
                )
                line = test_shows.readline().strip()
                self.assertEqual(
                    File_name_parser.guess_year(file_name), int(line)
                )
                line = test_shows.readline().strip()
                self.assertEqual(
                    File_name_parser.remove_user_tags(file_name), line
                )
                line = test_shows.readline().strip()
                self.assertEqual(
                    File_name_parser.remove_meta_tags(file_name), line
                )
                line = test_shows.readline().strip()
                self.assertEqual(
                    File_name_parser.remove_file_extension(file_name), line
                )
                line = test_shows.readline().strip()
                self.assertEqual(
                    File_name_parser.is_media(file_name),
                    line.lower() == "true"
                )
                line = test_shows.readline().strip()
                self.assertEqual(
                    File_name_parser.is_subtitle(file_name),
                    line.lower() == "true"
                )
                line = test_shows.readline().strip()
                self.assertEqual(
                    File_name_parser.is_oad(file_name),
                    line.lower() == "true"
                )
                line = test_shows.readline().strip()
                self.assertEqual(
                    File_name_parser.is_extra(file_name),
                    line.lower() == "true"
                )
                line = test_shows.readline().strip()
                self.assertEqual(
                    File_name_parser.is_ncop(file_name),
                    line.lower() == "true"
                )
                line = test_shows.readline().strip()
                self.assertEqual(
                    File_name_parser.is_nced(file_name),
                    line.lower() == "true"
                )
                line = test_shows.readline().strip()
                self.assertEqual(
                    File_name_parser.is_ova(file_name),
                    line.lower() == "true"
                )
                line = test_shows.readline()

    def test_movies(self):
        folder = "test" if __name__ != '__main__' else ""

        path = os.path.join(sys.path[0], folder, "test-movies")
        with open(path, "r") as test_movies:
            line = test_movies.readline()

            while line:
                if line.startswith('#') or not line.strip():
                    line = test_movies.readline()
                    continue
                elif line.strip() == "EOF":
                    break

                file_name = line.strip()

                line = test_movies.readline().strip()
                self.assertEqual(
                    File_name_parser.guess_show_name(file_name), line
                )
                line = test_movies.readline().strip()
                self.assertEqual(
                    File_name_parser.guess_year(file_name), int(line)
                )

                line = test_movies.readline()


if __name__ == '__main__':
    unittest.main()
