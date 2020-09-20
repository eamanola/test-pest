import sys
import os
sys.path.append(os.path.join(sys.path[0], os.path.join('classes', 'db')))


class DB(object):
    SQLITE = "sqlite"
    MARIADB = "mariadb"
    MYSQL = "mysql"

    TITLE_TO_ANIDB_ID = "title_to_anidb_id"
    TITLE_TO_IMDB_ID = "title_to_imdb_id"

    db_type = SQLITE

    def __init__(self):
        super(DB, self).__init__()

    def connect(self):
        raise NotImplementedError();

    def close(self):
        raise NotImplementedError();

    def create_title_to_anidb_id_table(self):
        raise NotImplementedError();

    def populate_title_to_anidb_id_table(self, data):
        raise NotImplementedError();

    def create_title_to_imdb_id_table(self):
        raise NotImplementedError();

    def populate_title_to_imdb_id_table(self, data):
        raise NotImplementedError();

    def get_anidb_ids(self, re_show_name):
        raise NotImplementedError();

    def get_imdb_ids(self, re_show_name):
        raise NotImplementedError();

    @staticmethod
    def get_instance():
        instance = None;

        if DB.db_type == DB.SQLITE:
            from sqlite import Sqlite
            instance = Sqlite()

        elif DB.db_type in (DB.MARIADB, DB.MYSQL):
            raise NotImplementedError();

        return instance;
