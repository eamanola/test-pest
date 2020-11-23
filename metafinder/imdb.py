import re
from metafinder.ext_api import Ext_api
from metafinder.ext_title_to_id_file_parser import Ext_title_to_id_file_parser


class IMDB(Ext_api):
    KEY = "imdb"
    TV_SHOW = "tvEpisode"
    MOVIE = "movie"
    TITLE_TO_ID_TABLE = "title_to_{}_id".format(KEY)
    # From https://datasets.imdbws.com/
    TITLE_TO_ID_FILE_PATH = "./external/imdb-titles-nightly-20200913"

    title_to_id_file_parser = None

    def __init__(self):
        super(IMDB, self).__init__()

    @staticmethod
    def get_title_to_id_file_parser():
        if IMDB.title_to_id_file_parser is None:
            IMDB.title_to_id_file_parser = Imdb_title_to_id_file_parser()

        return self.title_to_id_file_parser


class Imdb_title_to_id_file_parser(Ext_title_to_id_file_parser):
    def __init__(self):
        super(Imdb_title_to_id_file_parser, self).__init__()

    @staticmethod
    def parse_title_from_line(line):
        parts = line.strip().split("\t")
        return parts[2]

    @staticmethod
    def parse_id_from_line(line):
        parts = line.strip().split("\t")
        return parts[0]

    @staticmethod
    def parse_year_from_line(line):
        parts = line.strip().split("\t")

        if re.compile(r'^\d{4}$').match(parts[5]):
            year = int(parts[5])
        else:
            year = None

        return year

    @staticmethod
    def parse_media_type_from_line(line):
        parts = line.strip().split("\t")
        return parts[1]
