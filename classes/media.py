import sys
import os
sys.path.append(os.path.join(sys.path[0], '..'))
from classes.identifiable import Identifiable

class Media(object):
    def __init__(self, media_name):
        super(Media, self).__init__()

        self.media_name = media_name;
        self.file = None;
        self.subtitles = [];

class Episode(Media):
    def __init__(self, media_name):
        super(Episode, self).__init__(media_name)

class Movie(Media, Identifiable):
    def __init__(self, media_name):
        super(Movie, self).__init__(media_name)
        self.year = None;
