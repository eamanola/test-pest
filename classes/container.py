from classes.identifiable import Identifiable
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

    def id(hash_id):
        return hashlib.md5(hash_id.encode('utf-8')).hexdigest()

    def title(self):
        raise NotImplementedError()

    def poster(self):
        return ""

    def unplayed_count(self):
        return self._unplayed_count

    def set_unplayed_count(self, unplayed_count):
        self._unplayed_count = unplayed_count


class MediaLibrary(Container):
    def __init__(self, path, parent=None):
        super(MediaLibrary, self).__init__(parent=parent)
        self._path = path

    def path(self):
        return self._path

    def id(self):
        return Container.id(self.path())

    def title(self):
        return self.path()


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

    def title(self):
        return self.show_name()

    def poster(self):
        poster = None
        if self.meta() and self.meta().image_name():
            poster = f"/images/posters/{self.meta().image_name()}"

        return poster


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
            self.show_name(),
            "season",
            self.season_number()
        )
        return Container.id(id_str)

    def title(self):
        return "Season {:02d}".format(self.season_number())


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
            self.show_name(),
            "season",
            self.season_number(),
            "extra"
        )
        return Container.id(id_str)

    def title(self):
        return "Extra"
