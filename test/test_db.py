import unittest
from db.db import DB, get_db


class TestDB(unittest.TestCase):

    def test_db(self):
        self.assertEqual(DB.SQLITE, "sqlite")
        self.assertEqual(DB.MARIADB, "mariadb")
        self.assertEqual(DB.MYSQL, "mysql")
        self.assertEqual(DB.USE_DB, DB.SQLITE)
        self.assertRaises(NotImplementedError, DB().connect)
        self.assertRaises(NotImplementedError, DB().close)
        self.assertRaises(
            NotImplementedError,
            DB().populate_title_to_ext_id_table,
            "table",
            "data"
        )
        self.assertRaises(
            NotImplementedError, DB().get_ext_ids, "table", "re_show_name"
        )
        self.assertRaises(NotImplementedError, DB().create_containers_table)
        self.assertRaises(
            NotImplementedError,
            DB().update_containers,
            "containers",
            "update_identifiables=True"
        )
        self.assertRaises(
            NotImplementedError, DB().get_container, "container"
        )
        self.assertRaises(
            NotImplementedError, DB().delete_containers, "containers"
        )
        self.assertRaises(NotImplementedError, DB().create_media_table)
        self.assertRaises(
            NotImplementedError,
            DB().update_media,
            "media",
            "update_identifiables=True",
            "overwrite_media_states=True"
        )
        self.assertRaises(
            NotImplementedError, DB().get_media, "media"
        )
        self.assertRaises(
            NotImplementedError, DB().delete_media, "media"
        )
        self.assertRaises(NotImplementedError, DB().create_watchlist_table)
        self.assertRaises(
            NotImplementedError, DB().is_in_watchlists, "show_id"
        )
        self.assertRaises(
            NotImplementedError, DB().add_to_watchlist, "show_ids"
        )
        self.assertRaises(
            NotImplementedError, DB().remove_from_watchlist, "show_ids"
        )
        self.assertRaises(NotImplementedError, DB().remove_all_from_watchlist)
        self.assertRaises(NotImplementedError, DB().get_watchlist)
        self.assertRaises(
            NotImplementedError, DB().update_meta, "meta"
        )
        self.assertRaises(
            NotImplementedError, DB().get_unplayed_count, "container_id"
        )
        self.assertRaises(
            NotImplementedError, DB().set_played, "container_id", "played"
        )
        self.assertRaises(NotImplementedError, DB().last_modified)
        self.assertRaises(NotImplementedError, DB().version)

    def test_get_db(self):
        from db.sqlite import Sqlite

        DB.USE_DB = DB.MARIADB
        self.assertRaises(NotImplementedError, get_db)

        DB.USE_DB = DB.MYSQL
        self.assertRaises(NotImplementedError, get_db)

        DB.USE_DB = None
        self.assertRaises(NotImplementedError, get_db)

        DB.USE_DB = "foobar"
        self.assertRaises(NotImplementedError, get_db)

        DB.USE_DB = DB.SQLITE
        self.assertIsInstance(get_db(), Sqlite)


if __name__ == '__main__':
    unittest.main()
