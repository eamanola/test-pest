class DB(object):
    # DB types
    SQLITE = "sqlite"
    MARIADB = "mariadb"
    MYSQL = "mysql"

    db_type = SQLITE

    def __init__(self):
        super(DB, self).__init__()

    def connect(self):
        raise NotImplementedError()

    def close(self):
        raise NotImplementedError()

    def populate_title_to_ext_id_table(self, table, data):
        raise NotImplementedError()

    def get_ext_ids(self, table, re_show_name):
        raise NotImplementedError()

    def create_containers_table(self):
        raise NotImplementedError()

    def update_containers(self, containers, update_identifiables=True):
        raise NotImplementedError()

    def get_container(self, container):
        raise NotImplementedError()

    def delete_containers(self, containers):
        raise NotImplementedError()

    def create_media_table(self):
        raise NotImplementedError()

    def update_media(
        self,
        media,
        update_identifiables=True,
        overwrite_media_states=True
    ):
        raise NotImplementedError()

    def get_media(self, media):
        raise NotImplementedError()

    def delete_media(self, media):
        raise NotImplementedError()

    def create_watchlist_table(self):
        raise NotImplementedError()

    def is_in_watchlists(self, show_id):
        raise NotImplementedError()

    def add_to_watchlist(self, show_ids):
        raise NotImplementedError()

    def remove_from_watchlist(self, show_ids):
        raise NotImplementedError()

    def remove_all_from_watchlist(self):
        raise NotImplementedError()

    def get_watchlist(self):
        raise NotImplementedError()

    def update_meta(self, meta):
        raise NotImplementedError()

    def get_unplayed_count(self, container_id):
        raise NotImplementedError()

    def set_played(self, container_id, played):
        raise NotImplementedError()

    def last_modified(self):
        raise NotImplementedError()

    def version(self):
        raise NotImplementedError()

    @staticmethod
    def get_instance():
        instance = None

        if DB.db_type == DB.SQLITE:
            from classes.dbs.sqlite import Sqlite
            instance = Sqlite()

        elif DB.db_type in (DB.MARIADB, DB.MYSQL):
            raise NotImplementedError()

        else:
            raise NotImplementedError()

        return instance
