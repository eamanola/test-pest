from pathlib import Path
import sys
import os

debug = False
debug = True

file_names = set()

print('read test-shows:') if debug else ""
test_shows = open(os.path.join(sys.path[0], 'test', 'test-shows'), "r")

line = test_shows.readline()

while line:
    if line.startswith('#') or not line.strip():
        line = test_shows.readline()
        continue

    elif line.strip() == "EOF":
        break

    file_name = line.strip()
    print(file_name) if debug else ""
    file_names.add(file_name)

    remaining_test_lines = 15 - 1
    for i in range(remaining_test_lines):
        next(test_shows)

    line = test_shows.readline()

test_shows.close()

print("") if debug else ""

print('read test-movies:') if debug else ""
test_movies = open(os.path.join(sys.path[0], 'test', "test-movies"), "r")

line = test_movies.readline()

while line:
    if line.startswith('#') or not line.strip():
        line = test_movies.readline()
        continue

    elif line.strip() == "EOF":
        break

    file_name = line.strip()
    print(file_name) if debug else ""
    file_names.add(file_name)

    remaining_test_lines = 3 - 1
    for i in range(remaining_test_lines):
        next(test_movies)

    line = test_movies.readline()

test_movies.close()

print("") if debug else ""

print('read test-random:') if debug else ""
test_random = open(os.path.join(sys.path[0], 'test', "test-random"), "r")

line = test_random.readline()

while line:
    if line.startswith('#') or not line.strip():
        line = test_random.readline()
        continue

    elif line.strip() == "EOF":
        break

    file_name = line.strip()
    print(file_name) if debug else ""
    file_names.add(file_name)

    line = test_random.readline()

test_random.close()

print("") if debug else ""

print('touch test files:') if debug else ""

tmp_folder = os.path.join(sys.path[0], "tmp")

for file_name in file_names:
    print(file_name) if debug else ""

    path = Path(os.path.join(tmp_folder, file_name.replace("\n", "")))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.touch(exist_ok=True)

print('files created')
