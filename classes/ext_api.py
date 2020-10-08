class Ext_api(object):
    KEY = None
    TV_SHOW = "TV_SHOW"
    MOVIE = "MOVIE"
    TITLE_TO_ID_TABLE = None
    TITLE_TO_ID_FILE_PATH = None

    def __init__(self):
        super(Ext_api, self).__init__()

    @staticmethod
    def get_title_to_id_file_parser(self):
        raise NotImplementedError()

    @staticmethod
    def get_meta_getter(self, ext_id):
        raise NotImplementedError()
