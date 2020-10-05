import hashlib
from classes.container import Show, Season, Extra
from classes.identifiable import Identifiable
import os
import sys


class Media(object):

    def __init__(self, file_path, parent=None):
        super(Media, self).__init__()

        self._file_path = file_path
        self.subtitles = []
        self._parent = parent

    def file_path(self):
        return self._file_path

    def id(self):
        return hashlib.md5(self.file_path().encode('utf-8')).hexdigest()

    def parent(self):
        return self._parent

    def title(self):
        raise NotImplementedError()

    def thumbnail(self, thumbnail, create_ifmissing=True):
        ret = None

        if (
            create_ifmissing and
            thumbnail and
            self.file_path() and
            self.parent()
        ):
            THUMBNAIL_FOLDER = os.path.join(
                sys.path[0],
                'images',
                'thumbnails'
            )

            thumbnail_path = os.path.join(THUMBNAIL_FOLDER, f"{thumbnail}.png")

            if not os.path.exists(thumbnail_path):
                if not os.path.exists(THUMBNAIL_FOLDER):
                    os.makedirs(THUMBNAIL_FOLDER)

                mediafile_full_path = os.path.join(
                    self.parent().path(),
                    self.file_path()
                )

                cmd = f'''
                    ffmpeg -ss {{}} -i "{mediafile_full_path}" -vf scale=240:-1
                    -y -vframes 1 "{thumbnail_path}"
                '''.replace("\n", " ")
                time = "00:04:00.000"
                os.system(cmd.format(time))

                # video shorter than 4 min
                if not os.path.exists(thumbnail_path):
                    time = "00:00:10.000"
                    os.system(cmd.format(time))

            ret = "/images/thumbnails/{}.png".format(thumbnail)

        return ret


class Episode(Media):
    def __init__(
        self,
        file_path,
        episode_number,
        parent=None,
        is_oad=False,
        is_ncop=False,
        is_nced=False
    ):
        super(Episode, self).__init__(file_path, parent=parent)
        self._episode_number = episode_number
        self._is_oad = is_oad
        self._is_ncop = is_ncop
        self._is_nced = is_nced

    def episode_number(self):
        return self._episode_number

    def is_oad(self):
        return self._is_oad

    def is_ncop(self):
        return self._is_ncop

    def is_nced(self):
        return self._is_nced

    def title(self):
        if self.is_oad():
            prefix = "OAD"
        elif self.is_ncop():
            prefix = "NCOP"
        elif self.is_nced():
            prefix = "NCED"
        else:
            prefix = "Episode"

        return "{} {:02d}".format(
            prefix,
            self.episode_number()
        )

    def thumbnail(self, create_ifmissing=True):
        thumbnail = self.title()

        if self.parent() and isinstance(self.parent(), (Extra, Season, Show)):
            if isinstance(self.parent(), Extra):
                thumbnail = "Extra {}".format(thumbnail)

            if (
                isinstance(self.parent(), Season) and
                self.parent().season_number()
            ):
                thumbnail = "Season{} {}".format(
                    self.parent().season_number(),
                    thumbnail
                )

            if (
                isinstance(self.parent(), Show) and
                self.parent().show_name()
            ):
                thumbnail = "{} {}".format(
                    self.parent().show_name(),
                    thumbnail
                )

        thumbnail = thumbnail.replace(" ", ".")

        return super().thumbnail(thumbnail, create_ifmissing)


class Movie(Media, Identifiable):
    def __init__(self, file_path, title, parent=None):
        super(Movie, self).__init__(file_path, parent=parent)
        self._title = title

    def title(self):
        return self._title

    def thumbnail(self, create_ifmissing=True):
        if self.year():
            thumbnail = "{} ({})".format(self.title(), self.year())
        else:
            thumbnail = self.title()

        thumbnail = thumbnail.replace(" ", ".")

        return super().thumbnail(thumbnail, create_ifmissing)
