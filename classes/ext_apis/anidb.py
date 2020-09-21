import re
from classes.ext_api import Ext_api
from classes.ext_title_to_id_file_parser import Ext_title_to_id_file_parser


class AniDB(Ext_api):
    KEY = "anidb"
    TV_SHOW = None
    MOVIE = None
    TITLE_TO_ID_TABLE = "title_to_{}_id".format(KEY)
    # From https://wiki.anidb.net/API#Data_Dumps
    TITLE_TO_ID_FILE_PATH = "./external/anidb-titles-nightly-20200913"

    title_to_id_file_parser = None

    def __init__(self):
        super(AniDB, self).__init__()

    @staticmethod
    def get_title_to_id_file_parser():
        if AniDB.title_to_id_file_parser is None:
            AniDB.title_to_id_file_parser = Anidb_title_to_id_file_parser()

        return AniDB.title_to_id_file_parser


class Anidb_title_to_id_file_parser(Ext_title_to_id_file_parser):
    def __init__(self):
        super(Anidb_title_to_id_file_parser, self).__init__()

    @staticmethod
    def parse_title_from_line(line):
        parts = line.strip().split("|")
        return parts[len(parts) - 1]

    @staticmethod
    def parse_id_from_line(line):
        parts = line.strip().split("|")
        return parts[0]

    @staticmethod
    def parse_year_from_line(line):
        title = Anidb_title_to_id_file_parser.parse_title_from_line(line)
        year_re = re.compile(r'.*\((\d{4})\).*')
        year_group = year_re.match(title)
        if year_group:
            year = int(year_group.group(1))
        else:
            year = None

        return year

    @staticmethod
    def parse_media_type_from_line(line):
        return None
