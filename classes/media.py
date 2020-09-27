from classes.identifiable import Identifiable
import hashlib


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


class Movie(Media, Identifiable):
    def __init__(self, file_path, title, parent=None):
        super(Movie, self).__init__(file_path, parent=parent)
        self._title = title

    def title(self):
        return self._title
