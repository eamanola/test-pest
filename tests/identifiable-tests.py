from classes.identifiable import Identifiable

debug = True
debug = False

RANDOM_STR = "foo"
RANDOM_STR2 = "bar"
RANDOM_INT = 22
FAIL = "FAIL"
PASS = "PASS"

test_name = "Identifiable.ext_ids"
print(test_name) if debug else ""
identifiable = Identifiable()
if identifiable.ext_ids() != {}:
    print(test_name, FAIL)

test_name = "Identifiable.year"
print(test_name) if debug else ""
identifiable = Identifiable()
if identifiable.year() is not None:
    print(test_name, FAIL)
identifiable = Identifiable()
identifiable._year = RANDOM_INT
if identifiable.year() is not RANDOM_INT:
    print(test_name, FAIL)

test_name = "Identifiable.set_year"
print(test_name) if debug else ""
identifiable = Identifiable()
if identifiable.year() is not None:
    print(test_name, FAIL)
identifiable.set_year(RANDOM_INT)
if identifiable.year() is not RANDOM_INT:
    print(test_name, FAIL)

print("identifiable-tests: Successfully Completed")
