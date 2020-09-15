import sys
import os
sys.path.append(os.path.join(sys.path[0], '..'))
from classes.identifiable import Identifiable

debug = True;
debug = False;

RANDOM_STR = "foo"
RANDOM_STR2 = "bar"
RANDOM_INT = 22;
FAIL = "FAIL";
PASS = "PASS";

test_name = "Identifiable.anidb_id"
print(test_name) if debug else "";
identifiable = Identifiable();
if not identifiable.anidb_id == None:
  print(test_name, FAIL);
identifiable.anidb_id = RANDOM_STR;
if not identifiable.anidb_id == RANDOM_STR:
  print(test_name, FAIL);

test_name = "Show.imdb_id"
print(test_name) if debug else "";
identifiable = Identifiable();
if not identifiable.imdb_id == None:
  print(test_name, FAIL);
identifiable.imdb_id = RANDOM_STR;
if not identifiable.imdb_id == RANDOM_STR:
  print(test_name, FAIL);

print("identifiable-tests: Successfully Completed");
