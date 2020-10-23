import unittest
from classes.ext_title_to_id_file_parser import Ext_title_to_id_file_parser


class TestExt_title_to_id_file_parser(unittest.TestCase):

    def test_Ext_api(self):
        self.assertRaises(
            NotImplementedError,
            Ext_title_to_id_file_parser.parse_title_from_line,
            "line"
        )
        self.assertRaises(
            NotImplementedError,
            Ext_title_to_id_file_parser.parse_id_from_line,
            "line"
        )
        self.assertRaises(
            NotImplementedError,
            Ext_title_to_id_file_parser.parse_year_from_line,
            "line"
        )
        self.assertRaises(
            NotImplementedError,
            Ext_title_to_id_file_parser.parse_media_type_from_line,
            "line"
        )


if __name__ == '__main__':
    unittest.main()
