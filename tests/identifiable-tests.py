from classes.identifiable import Identifiable

debug = True
debug = False

RANDOM_STR = "foo"
RANDOM_STR2 = "bar"
RANDOM_INT = 22
FAIL = "FAIL"
PASS = "PASS"

test_name = "Identifiable.anidb_id"
print(test_name) if debug else ""
identifiable = Identifiable()
if identifiable.anidb_id is not None:
    print(test_name, FAIL)

identifiable.anidb_id = RANDOM_STR
if identifiable.anidb_id is not RANDOM_STR:
    print(test_name, FAIL)


test_name = "Identifiable.imdb_id"
print(test_name) if debug else ""
identifiable = Identifiable()
if identifiable.imdb_id is not None:
    print(test_name, FAIL)

identifiable.imdb_id = RANDOM_STR
if identifiable.imdb_id is not RANDOM_STR:
    print(test_name, FAIL)


test_name = "Identifiable.year"
print(test_name) if debug else ""
identifiable = Identifiable()
if identifiable.year is not None:
    print(test_name, FAIL)
identifiable.year = RANDOM_INT
if identifiable.year is not RANDOM_INT:
    print(test_name, FAIL)

print("identifiable-tests: Successfully Completed")
