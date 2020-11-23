import unittest
from metafinder.ext_api import Ext_api


class TestExt_api(unittest.TestCase):

    def test_Ext_api(self):
        self.assertIsNone(Ext_api.KEY)
        self.assertEqual(Ext_api.TV_SHOW, "TV_SHOW")
        self.assertEqual(Ext_api.MOVIE, "MOVIE")
        self.assertIsNone(Ext_api.TITLE_TO_ID_TABLE)
        self.assertIsNone(Ext_api.TITLE_TO_ID_FILE_PATH)
        self.assertRaises(
            NotImplementedError,
            Ext_api.get_title_to_id_file_parser
        )
        self.assertRaises(
            NotImplementedError,
            Ext_api.get_meta_getter,
            "ext_id"
        )


if __name__ == '__main__':
    unittest.main()
