import re
from classes.db import DB

debug = True
debug = False


class Identifier(object):
    def __init__(self, ext_api):
        super(Identifier, self).__init__()
        self.ext_api = ext_api

    def search_db(self, db, show_name, keep_year):
        re_search = Identifier.compile_re_search(
            show_name,
            exact_match=False,
            keep_year=keep_year
        )
        print('Searching for:', re_search) if debug else ""

        matches = db.get_ext_ids(self.ext_api.TITLE_TO_ID_TABLE, re_search)

        Identifier.print_result(matches) if debug else ""

        return matches

    def guess_id(
        self,
        db,
        show_name,
        year,
        media_type
    ):
        print("Showname: '{}'".format(show_name)) if debug else ""
        ext_id = None

        matches = self.search_db(db, show_name, keep_year=True)
        if len(matches) == 0:
            matches = self.search_db(db, show_name, keep_year=False)

        ext_id = matches[0][0] if len(matches) == 1 else None

        if ext_id is None and len(matches) > 0 and year is not None:

            year_matches = Identifier.filter_by_year(matches, year)
            match_count = len(year_matches)

            matches = year_matches if match_count > 0 else matches

            ext_id = matches[0][0] if match_count == 1 else None

        if ext_id is None and len(matches) > 0:

            exact_matches = Identifier.filter_by_exact_match(
                matches,
                show_name
            )
            match_count = len(exact_matches)

            matches = exact_matches if match_count > 0 else matches

            ext_id = matches[0][0] if match_count == 1 else None

        if ext_id is None and len(matches) > 0 and media_type is not None:

            media_type_matches = Identifier.filter_by_media_type(
                matches,
                media_type
            )
            match_count = len(media_type_matches)

            matches = media_type_matches if match_count > 0 else matches

            ext_id = matches[0][0] if match_count == 1 else None

        if ext_id is None and len(matches) > 0:

            unique_matches = Identifier.group_by_id(matches)
            match_count = len(unique_matches)

            matches = unique_matches if match_count > 0 else matches

            ext_id = matches[0][0] if match_count == 1 else None

            if match_count > 1:  # TODO: more filters?
                print(match_count, "unique matches for:", show_name)
                print("Selecting 1st:", unique_matches[0])
                for unique_match in unique_matches:
                    print(unique_match)
                print("")
                ext_id = matches[0][0]

        return ext_id

    @staticmethod
    def compile_re_search(show_name, exact_match, keep_year=False):
        re_search_str = show_name

        re_search_str = re.sub(
            r'[^a-z]s\s*\d+(?:[^a-z]|$)',
            ".",
            re_search_str,
            flags=re.IGNORECASE
        )
        re_search_str = re.sub(
            '[^a-zA-Z]part[^a-zA-Z]',
            ".",
            re_search_str,
            flags=re.IGNORECASE
        )
        re_search_str = re.sub(
            '[^a-zA-Z]ova(?:[^a-zA-Z]|$)',
            ".",
            re_search_str,
            flags=re.IGNORECASE
        )
        re_search_str = re.sub(
            r'(?:season)+s?\s?\d+',
            ".",
            re_search_str,
            flags=re.IGNORECASE
        )

        r_simple_year = r'\(\d{4}\)' if keep_year else ""
        r_extra_characters = fr'[^A-Za-z{r_simple_year}]+'

        re_search_str = re.sub(r_extra_characters, ".+", re_search_str)
        re_search_str = re.sub(r'^\.(?:\*|\+)', "", re_search_str)
        re_search_str = re.sub(r'\.(?:\*|\+)$', "", re_search_str)
        re_search_str = re.sub(r'\)', "\\)", re_search_str)
        re_search_str = re.sub(r'\(', "\\(", re_search_str)

        if exact_match:
            re_search_str = "^" + re_search_str + "$"
        else:
            re_search_str = ".*" + re_search_str + ".*"

        return re.compile(re_search_str, re.IGNORECASE)

    @staticmethod
    def print_result(matches):
        match_count = len(matches)

        if match_count == 0:
            result_str = "No matches found."
        elif match_count == 1:
            result_str = "Single match: {}".format(tuple(matches[0]))
        else:
            result_str = "{} matches found.".format(match_count)

        print(result_str)

        line = ""
        for _ in range(len(result_str)):
            line = line + "-"
        print(line)

        print("")

    @staticmethod
    def filter_by_year(matches, year):
        print("Filtering by year:") if debug else ""

        year_matches = [m for m in matches if m[2] == year]

        Identifier.print_result(year_matches) if debug else ""

        return year_matches

    @staticmethod
    def filter_by_exact_match(matches, show_name):
        print("Looking for exact matches:") if debug else ""

        re_search = Identifier.compile_re_search(
            show_name,
            exact_match=True,
            keep_year=True
        )
        print('Searching for:', re_search) if debug else ""

        exact_matches = [m for m in matches if re_search.match(m[1])]

        Identifier.print_result(exact_matches) if debug else ""

        return exact_matches

    @staticmethod
    def filter_by_media_type(matches, media_type):
        print("Filtering by media type:") if debug else ""

        media_type_matches = [m for m in matches if m[3] == media_type]

        Identifier.print_result(media_type_matches) if debug else ""

        return media_type_matches

    @staticmethod
    def group_by_id(matches):
        print("Grouping by ids:") if debug else ""

        unique_matches = []
        for match in matches:
            print('*', tuple(match)) if debug else ""
            ani_id = match[0]
            found = False
            for unique_match in unique_matches:
                if(unique_match[0] == ani_id):
                    found = True
                    break
            if found is False:
                print('--unique match.') if debug else ""
                unique_matches.append(match)

        Identifier.print_result(unique_matches) if debug else ""
        return unique_matches
