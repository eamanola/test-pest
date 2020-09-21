from classes.ext_title_to_id_file_parser import Ext_title_to_id_file_parser

debug = True
debug = False

RANDOM_STR = "foo"
RANDOM_STR2 = "bar"
RANDOM_INT = 22
FAIL = "FAIL"
PASS = "PASS"

test_name = "Ext_title_to_id_file_parser.parse_title_from_line"
print(test_name) if debug else ""
try:
    Ext_title_to_id_file_parser.parse_title_from_line(RANDOM_STR)
    print(test_name, FAIL)
except Exception as e:
    if not isinstance(e, NotImplementedError):
        print(test_name, FAIL, e)

test_name = "Ext_title_to_id_file_parser.parse_id_from_line"
print(test_name) if debug else ""
try:
    Ext_title_to_id_file_parser.parse_id_from_line(RANDOM_STR)
    print(test_name, FAIL)
except Exception as e:
    if not isinstance(e, NotImplementedError):
        print(test_name, FAIL, e)

test_name = "Ext_title_to_id_file_parser.parse_year_from_line"
print(test_name) if debug else ""
try:
    Ext_title_to_id_file_parser.parse_year_from_line(RANDOM_STR)
    print(test_name, FAIL)
except Exception as e:
    if not isinstance(e, NotImplementedError):
        print(test_name, FAIL, e)

test_name = "Ext_title_to_id_file_parser.parse_media_type_from_line"
print(test_name) if debug else ""
try:
    Ext_title_to_id_file_parser.parse_media_type_from_line(RANDOM_STR)
    print(test_name, FAIL)
except Exception as e:
    if not isinstance(e, NotImplementedError):
        print(test_name, FAIL, e)

print("ext_title_to_id_file_parser-tests: Successfully Completed")
