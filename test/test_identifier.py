import unittest
from classes.identifier import Identifier


class TestIdentifier(unittest.TestCase):

    def test_search_db(self):
        from classes.dbs.sqlite import Sqlite
        from classes.ext_api import Ext_api
        db = Sqlite()
        db.connect(database=":memory:")

        ext_api = Ext_api()
        ext_api.TITLE_TO_ID_TABLE = "randomtable"

        data = [
            ('ext_id',  "foo",             2000, 'media_type'),
            ('ext_id',  "foobar",          1999, 'media_type2'),
            ('ext_id',  "foobar (2000)",   2000, 'media_type'),
            ('ext_id1', "foobar (2001)",   2001, 'media_type')
        ]

        db.populate_title_to_ext_id_table(ext_api.TITLE_TO_ID_TABLE, data)

        identifier = Identifier(ext_api)

        matches = identifier.search_db(db, "foo (2000)", year=None)
        self.assertEqual(len(matches), 4)

        matches = identifier.search_db(db, "foobar (2001)", year=None)
        self.assertEqual(len(matches), 3)

        matches = identifier.search_db(db, "foobar (2001)", year=2001)
        self.assertEqual(len(matches), 1)

        db.close()

    def test_compile_re_search(self):
        show_name = """
            !!! foo !! (2000) !!...
            """
        re1 = Identifier.compile_re_search(
            show_name, exact_match=False, year=None
        )

        self.assertIsNotNone(re1.search("foo (2001)"))

        re1 = Identifier.compile_re_search(
            show_name, exact_match=False, year=2000
        )
        self.assertIsNone(re1.search("foo"))
        self.assertIsNotNone(re1.search("foo (2000)"))

        re1 = Identifier.compile_re_search(
            show_name, exact_match=True, year=None
        )

        self.assertIsNotNone(re1.search("foo"))
        self.assertIsNone(re1.search("a foo bar"))

    def test_filter_by_year(self):
        data = [
            ('ext_id',  "foo",             2000, 'media_type'),
            ('ext_id',  "foobar",          1999, 'media_type2'),
            ('ext_id',  "foobar (2000)",   2000, 'media_type'),
            ('ext_id1', "foobar (2001)",   2001, 'media_type')
        ]

        matches = Identifier.filter_by_year(data, 2000)
        self.assertEqual(len(matches), 2)

        matches = Identifier.filter_by_year(data, 2001)
        self.assertEqual(len(matches), 1)

        matches = Identifier.filter_by_year(data, 1000)
        self.assertEqual(len(matches), 0)

    def test_filter_by_exact_match(self):
        data = [
            ('ext_id',  "foo",             2000, 'media_type'),
            ('ext_id',  "foobar",          1999, 'media_type2'),
            ('ext_id',  "foobar (2000)",   2000, 'media_type'),
            ('ext_id1', "foobar (2001)",   2001, 'media_type')
        ]

        matches = Identifier.filter_by_exact_match(data, "foo", year=None)
        self.assertEqual(len(matches), 1)

        matches = Identifier.filter_by_exact_match(data, "foobar", year=None)
        self.assertEqual(len(matches), 1)

        matches = Identifier.filter_by_exact_match(data, "foobar", year=2000)
        self.assertEqual(len(matches), 1)

        matches = Identifier.filter_by_exact_match(data, "foobar", year=2001)
        self.assertEqual(len(matches), 1)

        matches = Identifier.filter_by_exact_match(data, "bar", year=None)
        self.assertEqual(len(matches), 0)

    def test_filter_by_media_type(self):
        data = [
            ('ext_id',  "foo",             2000, 'media_type'),
            ('ext_id',  "foobar",          1999, 'media_type2'),
            ('ext_id',  "foobar (2000)",   2000, 'media_type'),
            ('ext_id1', "foobar (2001)",   2001, 'media_type')
        ]

        matches = Identifier.filter_by_media_type(data, "media_type")
        self.assertEqual(len(matches), 3)

        matches = Identifier.filter_by_media_type(data, "media_type2")
        self.assertEqual(len(matches), 1)

        matches = Identifier.filter_by_media_type(data, "media_type3")
        self.assertEqual(len(matches), 0)

    def test_group_by_id(self):
        data = [
            ('ext_id',  "foo",             2000, 'media_type'),
            ('ext_id',  "foobar",          1999, 'media_type2'),
            ('ext_id',  "foobar (2000)",   2000, 'media_type'),
            ('ext_id1', "foobar (2001)",   2001, 'media_type')
        ]

        unique_matches = Identifier.group_by_id(data)
        self.assertEqual(len(unique_matches), 2)


if __name__ == '__main__':
    unittest.main()
