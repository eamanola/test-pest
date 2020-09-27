from classes.identifiable import Identifiable
import hashlib


class Container(object):
    def __init__(self, parent=None):
        super(Container, self).__init__()

        self.containers = []
        self.media = []
        self._parent = parent

    def parent(self):
        return self._parent

    def get_container(self, container_id):
        for container in self.containers:
            if container.id() == container_id:
                return container

        return None

    def get_media(self, media_id):
        for media in self.media:
            if media.id() == media_id:
                return media

        return None

    def id(hash_id):
        return hashlib.md5(hash_id.encode('utf-8')).hexdigest()


class MediaLibrary(Container):
    def __init__(self, path, parent=None):
        super(MediaLibrary, self).__init__(parent=parent)
        self._path = path

    def path(self):
        return self._path

    def id(self):
        return Container.id(self.path())


class Show(MediaLibrary, Identifiable):
    def __init__(self, library_path, show_name, parent=None):
        super(Show, self).__init__(library_path, parent=parent)
        self._show_name = show_name

    def show_name(self):
        return self._show_name

    def seasons(self):
        return self.containers

    def id(self):
        return Container.id(self.show_name())


class Season(Show):
    def __init__(self, library_path, show_name, season_number, parent=None):
        super(Season, self).__init__(library_path, show_name, parent=parent)
        self._season_number = season_number

    def seasons(self):
        return None

    def extras(self):
        return self.containers

    def episodes(self):
        return self.media

    def season_number(self):
        return self._season_number

    def id(self):
        id_str = "{}{}{}".format(
            self.show_name(), "season", self.season_number()
        )
        return Container.id(id_str)


class Extra(Season):
    def __init__(self, library_path, show_name, season_number, parent=None):
        super(Extra, self).__init__(
            library_path,
            show_name,
            season_number,
            parent=parent
        )

    def extras(self):
        return None

    def id(self):
        id_str = "{}{}{}{}".format(
            self.show_name(), "season", self.season_number(), "extra"
        )
        return Container.id(id_str)
