import re

class Ext_title_to_id_file_parser(object):
    TV_SHOW = None
    MOVIE = None

    def __init__(self):
        super(Ext_title_to_id_file_parser, self).__init__()
        self.file_path = None

    @staticmethod
    def parse_title_from_line(line):
        raise NotImplementedError();
    @staticmethod
    def parse_id_from_line(line):
        raise NotImplementedError();
    @staticmethod
    def parse_year_from_line(line):
        raise NotImplementedError();
    @staticmethod
    def parse_media_type_from_line(line):
        raise NotImplementedError()

class Anidb_title_to_id_file_parser(Ext_title_to_id_file_parser):
    TV_SHOW = None
    MOVIE = None

    def __init__(self):
        super(Anidb_title_to_id_file_parser, self).__init__()

        #From https://wiki.anidb.net/API#Data_Dumps
        self.file_path = "./external/anidb-titles-nightly-20200913"

    @staticmethod
    def parse_title_from_line(line):
        parts = line.strip().split("|");
        return parts[len(parts) - 1];

    @staticmethod
    def parse_id_from_line(line):
        parts = line.strip().split("|");
        return parts[0];

    @staticmethod
    def parse_year_from_line(line):
        title = Anidb_title_to_id_file_parser.parse_title_from_line(line);
        year_re = re.compile('.*\((\d{4})\).*');
        year_group = year_re.match(title);
        if year_group:
            year = int(year_group.group(1));
        else:
            year = None;

        return year;

    @staticmethod
    def parse_media_type_from_line(line):
        return None;

class Imdb_title_to_id_file_parser(Ext_title_to_id_file_parser):
    TV_SHOW = "tvEpisode";
    MOVIE = "movie"

    def __init__(self):
        super(Imdb_title_to_id_file_parser, self).__init__()

        #From https://datasets.imdbws.com/
        self.file_path = "./external/imdb-titles-nightly-20200913"

    @staticmethod
    def parse_title_from_line(line):
        parts = line.strip().split("\t");
        return parts[2];

    @staticmethod
    def parse_id_from_line(line):
        parts = line.strip().split("\t");
        return parts[0];

    @staticmethod
    def parse_year_from_line(line):
        parts = line.strip().split("\t");

        if re.compile('^\d{4}$').match(parts[5]):
            year = int(parts[5]);
        else:
             year = None;

        return year;

    @staticmethod
    def parse_media_type_from_line(line):
        parts = line.strip().split("\t");
        return parts[1];
