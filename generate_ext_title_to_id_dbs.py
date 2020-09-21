from classes.db import DB
from classes.ext_apis.anidb import AniDB
from classes.ext_apis.imdb import IMDB


def parse_file(file_path, parser):
    results = []

    file = open(file_path, "r")
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


# ext_api = AniDB
# ext_api = IMDB()
def generate_table(ext_api):
    if ext_api:
        parser = ext_api.get_title_to_id_file_parser()
        table = ext_api.TITLE_TO_ID_TABLE
        file_path = ext_api.TITLE_TO_ID_FILE_PATH

    if parser and table:
        results = parse_file(file_path, parser)
        db = DB.get_instance()
        db.connect()
        db.create_title_to_ext_id_table(table)
        db.populate_title_to_ext_id_table(table, results)
        db.print_table(table)
        db.close()

generate_table(AniDB)
