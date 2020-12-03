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

    def get_episode(self, episode):
        from models.containers import Season
        meta = None

        for episode_meta in self.episodes():
            if episode.episode_number():
                if (
                    episode_meta.season_number() <= 0
                    or (episode.parent()
                        and isinstance(episode.parent(), Season)
                        and episode.parent().season_number() ==
                        episode_meta.season_number())
                ) and (
                    episode_meta.episode_number() == episode.episode_number()
                ):
                    meta = episode_meta
                    break

        return meta


class Episode_Meta(object):

    def __init__(self, episode_number, season_number, title, summary):
        super(Episode_Meta, self).__init__()

        self._episode_number = episode_number
        self._season_number = season_number
        self._title = title
        self._summary = summary

    def episode_number(self):
        return self._episode_number

    def season_number(self):
        return self._season_number

    def title(self):
        return self._title

    def summary(self):
        return self._summary
