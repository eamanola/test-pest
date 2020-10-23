import unittest
from classes.db import DB


class TestDB(unittest.TestCase):

    def test_db(self):
        self.assertEqual(DB.SQLITE, "sqlite")
        self.assertEqual(DB.MARIADB, "mariadb")
        self.assertEqual(DB.MYSQL, "mysql")
        self.assertEqual(DB.db_type, DB.SQLITE)
        self.assertRaises(NotImplementedError, DB().connect)
        self.assertRaises(NotImplementedError, DB().close)
        self.assertRaises(
            NotImplementedError,
            DB().populate_title_to_ext_id_table,
            "table", "data"
        )
        self.assertRaises(
            NotImplementedError,
            DB().get_ext_ids,
            "table", "re_show_name"
        )
        self.assertRaises(NotImplementedError, DB().create_containers_table)
        self.assertRaises(
            NotImplementedError,
            DB().update_containers,
            "containers",
            "update_identifiables=True"
        )
        self.assertRaises(
            NotImplementedError,
            DB().get_container,
            "container"
        )
        self.assertRaises(
            NotImplementedError,
            DB().delete_containers,
            "containers"
        )
        self.assertRaises(NotImplementedError, DB().create_media_table)
        self.assertRaises(
            NotImplementedError,
            DB().update_media,
            "media", "update_identifiables=True", "overwrite_media_states=True"
        )
        self.assertRaises(
            NotImplementedError,
            DB().get_media,
            "media"
        )
        self.assertRaises(
            NotImplementedError,
            DB().delete_media,
            "media"
        )
        self.assertRaises(NotImplementedError, DB().create_watchlist_table)
        self.assertRaises(
            NotImplementedError,
            DB().is_in_watchlists,
            "show_id"
        )
        self.assertRaises(
            NotImplementedError,
            DB().add_to_watchlist,
            "show_ids"
        )
        self.assertRaises(
            NotImplementedError,
            DB().remove_from_watchlist,
            "show_ids"
        )
        self.assertRaises(NotImplementedError, DB().get_watchlist)
        self.assertRaises(
            NotImplementedError,
            DB().update_meta,
            "meta"
        )
        self.assertRaises(
            NotImplementedError,
            DB().get_unplayed_count,
            "container_id"
        )

    def test_get_instance(self):
        from classes.dbs.sqlite import Sqlite
        DB.db_type = DB.SQLITE
        self.assertIsInstance(DB.get_instance(), Sqlite)

        DB.db_type = DB.MARIADB
        self.assertRaises(NotImplementedError, DB.get_instance)

        DB.db_type = DB.MYSQL
        self.assertRaises(NotImplementedError, DB.get_instance)

        DB.db_type = None
        self.assertRaises(NotImplementedError, DB.get_instance)

        DB.db_type = "foobar"
        self.assertRaises(NotImplementedError, DB.get_instance)


if __name__ == '__main__':
    unittest.main()
