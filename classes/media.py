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
    def __init__(self, file_path, episode_number, parent=None):
        super(Episode, self).__init__(parent)
        self._episode_number = episode_number

    def episode_number(self):
        return self._episode_number


class Movie(Media, Identifiable):
    def __init__(self, file_path, title, parent=None):
        super(Movie, self).__init__(parent)
        self._title = title

    def title(self):
        return self._title
