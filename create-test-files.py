from pathlib import Path

debug = False;
debug = True;

file_names = [];

print('read test-shows:') if debug else "";
test_shows = open("test-shows", "r");

line = test_shows.readline();

while line:
    if line.startswith('#') or not line.strip():
        line = test_shows.readline();
        continue;

    elif line.strip() == "EOF":
        break;

    file_name = line.strip();
    print(file_name) if debug else "";
    file_names.append(file_name);

    remaining_test_lines = 11;
    for i in range(remaining_test_lines):
        next(test_shows);

    line = test_shows.readline();

test_shows.close();

print("") if debug else "";

print('read test-movies:') if debug else "";
test_movies = open("test-movies", "r");

line = test_movies.readline();

while line:
    if line.startswith('#') or not line.strip():
        line = test_movies.readline();
        continue;
        
    elif line.strip() == "EOF":
        break;

    file_name = line.strip();
    print(file_name) if debug else "";
    file_names.append(file_name);

    remaining_test_lines = 2;
    for i in range(remaining_test_lines):
        next(test_movies);

    line = test_movies.readline();

test_movies.close();

print("") if debug else "";

print('touch test files:') if debug else "";

tmp_folder = "./tmp/";
#Path(tmp_folder + "*").unlink(missing_ok=True);

for file_name in file_names:
    print(file_name) if debug else "";

    path = tmp_folder + (file_name.replace("\n", ""));
    Path(path).parent.mkdir(exist_ok=True, parents=True);
    Path(path).touch(exist_ok=True);

print('files created');
