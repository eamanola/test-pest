import hashlib
from models.containers import Show, Season, Extra
from models.identifiable import Identifiable


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

    def thumbnail(self):
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
        is_nced=False,
        is_ova=False
    ):
        super(Episode, self).__init__(file_path, played, parent=parent)
        self._episode_number = episode_number
        self._is_oad = is_oad
        self._is_ncop = is_ncop
        self._is_nced = is_nced
        self._is_ova = is_ova

    def episode_number(self):
        return self._episode_number

    def is_oad(self):
        return self._is_oad

    def is_ncop(self):
        return self._is_ncop

    def is_nced(self):
        return self._is_nced

    def is_ova(self):
        return self._is_ova

    def is_extra(self):
        return (
            self.is_oad()
            or self.is_ncop()
            or self.is_nced()
            or self.is_ova()
            or (self.parent() and isinstance(self.parent(), Extra))
        )

    def title(self):
        if self.is_oad():
            prefix = "OAD"
        elif self.is_ncop():
            prefix = "NCOP"
        elif self.is_nced():
            prefix = "NCED"
        elif self.is_ova():
            prefix = "OVA"
        elif self.is_extra():
            prefix = "Extra"
        else:
            prefix = "Episode"

        if self.episode_number():
            title = "{} {:02d}".format(prefix, self.episode_number())
        else:
            title = prefix

        return title

    def thumbnail(self):
        import re
        thumbnail = self.title()

        parent = self.parent()

        while parent and isinstance(parent, (Extra, Season, Show)):
            thumbnail = f"{parent.title()} {thumbnail}"
            parent = parent.parent()

        thumbnail = re.sub(r'[^a-zA-Z0-9]', ".", thumbnail)
        thumbnail = re.sub(r'\.+', ".", thumbnail)

        return thumbnail


class Movie(Media, Identifiable):
    def __init__(self, file_path, title, played, parent=None):
        super(Movie, self).__init__(file_path, played, parent=parent)
        self._title = title

    def title(self):
        return self._title

    def thumbnail(self):
        thumbnail = self.title()

        thumbnail = thumbnail.replace(" ", ".")

        return thumbnail
