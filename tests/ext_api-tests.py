from classes.ext_api import Ext_api

debug = True
debug = False

RANDOM_STR = "foo"
RANDOM_STR2 = "bar"
RANDOM_INT = 22
FAIL = "FAIL"
PASS = "PASS"

test_name = "Ext_api.get_title_to_id_file_parser"
print(test_name) if debug else ""
try:
    Ext_api.get_title_to_id_file_parser(RANDOM_STR)
    print(test_name, FAIL)
except Exception as e:
    if not isinstance(e, NotImplementedError):
        print(test_name, FAIL, e)

print("ext_api-tests: Successfully Completed")
