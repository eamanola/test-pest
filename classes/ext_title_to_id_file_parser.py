class Ext_title_to_id_file_parser(object):
    def __init__(self):
        super(Ext_title_to_id_file_parser, self).__init__()

    @staticmethod
    def parse_title_from_line(line):
        raise NotImplementedError()

    @staticmethod
    def parse_id_from_line(line):
        raise NotImplementedError()

    @staticmethod
    def parse_year_from_line(line):
        raise NotImplementedError()

    @staticmethod
    def parse_media_type_from_line(line):
        raise NotImplementedError()
