from classes.db import DB
from classes.ext_title_to_id_file_parser import (
    Anidb_title_to_id_file_parser,
    Imdb_title_to_id_file_parser
)


def parse_file(parser):
    results = []

    file = open(parser.file_path, "r")
    line = file.readline()

    while line:
        title = parser.parse_title_from_line(line)
        ext_id = parser.parse_id_from_line(line)
        year = parser.parse_year_from_line(line)
        media_type = parser.parse_media_type_from_line(line)

        result = (
            ext_id if ext_id else "",
            title if title else "",
            year if year else 0,
            media_type if media_type else ""
        )

        results.append(result)

        line = file.readline()

    file.close()

    return results


results = parse_file(Anidb_title_to_id_file_parser())
# results = parse_file(Imdb_title_to_id_file_parser())

db = DB.get_instance()
db.connect()

db.create_title_to_anidb_id_table()
db.populate_title_to_anidb_id_table(results)

# db.create_title_to_imdb_id_table()
# db.populate_title_to_imdb_id_table(results)

table = DB.TITLE_TO_ANIDB_ID
# table = DB.TITLE_TO_IMDB_ID
db.print_table(table)

db.close()
