import hashlib
from classes.container import Show, Season, Extra
from classes.identifiable import Identifiable


class Media(object):

    def __init__(self, file_path, played, parent=None):
        super(Media, self).__init__()

        self._file_path = file_path
        self.subtitles = []
        self._parent = parent
        self._played = played

    def file_path(self):
        return self._file_path

    def id(self):
        return hashlib.md5(self.file_path().encode('utf-8')).hexdigest()

    def parent(self):
        return self._parent

    def set_parent(self, parent):
        self._parent = parent

    def played(self):
        return self._played

    def set_played(self, played):
        self._played = played

    def title(self):
        raise NotImplementedError()

    def thumbnail(self, thumbnail):
        raise NotImplementedError()


class Episode(Media):
    def __init__(
        self,
        file_path,
        episode_number,
        played,
        parent=None,
        is_oad=False,
        is_ncop=False,
        is_nced=False
    ):
        super(Episode, self).__init__(file_path, played, parent=parent)
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

        if self.episode_number():
            title = "{} {:02d}".format(prefix, self.episode_number())
        else:
            title = prefix

        return title

    def thumbnail(self):
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

        return thumbnail


class Movie(Media, Identifiable):
    def __init__(self, file_path, title, played, parent=None):
        super(Movie, self).__init__(file_path, played, parent=parent)
        self._title = title

    def title(self):
        return self._title

    def thumbnail(self, create_ifmissing=True):
        if self.year():
            thumbnail = "{} ({})".format(self.title(), self.year())
        else:
            thumbnail = self.title()

        thumbnail = thumbnail.replace(" ", ".")

        return thumbnail
