class Meta(object):

    def __init__(self, id, title, rating, image_name, episodes, description):
        super(Meta, self).__init__()

        self._id = id
        self._title = title
        self._rating = rating
        self._image_name = image_name
        self._episodes = episodes
        self._description = description

    def id(self):
        return self._id

    def title(self):
        return self._title

    def rating(self):
        return self._rating

    def image_name(self):
        return self._image_name

    def episodes(self):
        return self._episodes

    def description(self):
        return self._description
