class Container(object):
    def __init__(self, container_name = None):
        super(Container, self).__init__()

        self.containers = []
        self.media = []
        self.container_name = container_name

    def get_container(self, container_name):
        for container in self.containers:
            if container.container_name == container_name:
                return container;

        return None;

    def get_media(self, media_name):
        for media in self.media:
            if media.media_name == media_name:
                return media;

        return None;

class Show(Container):
    def __init__(self, show_name = None):
        super(Show, self).__init__(show_name)
        self.year = None;

    def show_name(self):
        return self.container_name;

    def seasons(self):
        return self.containers;

class Season(Show):
    def __init__(self, season_name = None):
        super(Season, self).__init__(season_name)

    def seasons(self):
        return None;

    def season_name(self):
        return self.container_name;

    def extras(self):
        return self.containers;

    def episodes(self):
        return self.media;

class Extra(Season):
    def __init__(self, extra_name = None):
        super(Extra, self).__init__(extra_name)

    def extras(self):
        return None;
