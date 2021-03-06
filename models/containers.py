from models.identifiable import Identifiable
import hashlib


class Container(object):
    def __init__(self, parent=None):
        super(Container, self).__init__()

        self.containers = []
        self.media = []
        self._parent = parent
        self._unplayed_count = 0

    def parent(self):
        return self._parent

    def set_parent(self, parent):
        self._parent = parent

    def get_container(self, container_id):
        for container in self.containers:
            if container.id() == container_id:
                return container

        return None

    def find_container(self, container_id):
        match = None

        for container in self.containers:
            if container.id() == container_id:
                match = container
            else:
                match = container.find_container(container_id)

            if match:
                break

        return match

    def get_media(self, media_id):
        for media in self.media:
            if media.id() == media_id:
                return media

        return None

    def id(self):
        raise NotImplementedError()

    def hash_id(self, hash_id):
        return hashlib.md5(hash_id.encode('utf-8')).hexdigest()

    def title(self):
        raise NotImplementedError()

    def unplayed_count(self):
        return self._unplayed_count

    def set_unplayed_count(self, unplayed_count):
        self._unplayed_count = unplayed_count


class MediaLibrary(Container):
    def __init__(self, path, parent=None):
        super(MediaLibrary, self).__init__(parent=parent)
        self._path = path

    def id(self):
        return self.hash_id(self.path())

    def title(self):
        return self.path()

    def path(self):
        return self._path


class Show(MediaLibrary, Identifiable):
    def __init__(self, library_path, show_name, parent=None):
        super(Show, self).__init__(library_path, parent=parent)
        self._show_name = show_name

    def id(self):
        return self.hash_id(self.title())

    def title(self):
        title = self.show_name()

        if self.year():
            title = f'{title} ({self.year()})'

        return title

    def show_name(self):
        return self._show_name


class Season(Show):
    def __init__(self, library_path, show_name, season_number, parent=None):
        super(Season, self).__init__(library_path, show_name, parent=parent)
        self._season_number = season_number

    def id(self):
        id_str = "{}{}{}".format(
            self.show_name(),
            "season",
            self.season_number()
        )
        return self.hash_id(id_str)

    def title(self):
        return "Season {:02d}".format(self.season_number())

    def season_number(self):
        return self._season_number


class Extra(Season):
    def __init__(self, library_path, show_name, season_number, parent=None):
        super(Extra, self).__init__(
            library_path,
            show_name,
            season_number,
            parent=parent
        )

    def id(self):
        id_str = "{}{}{}{}".format(
            self.show_name(),
            "season",
            self.season_number(),
            "extra"
        )
        return self.hash_id(id_str)

    def title(self):
        return "Extra"
