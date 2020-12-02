import re

debug = True
debug = False


class Identifier(object):
    def __init__(self):
        super(Identifier, self).__init__()

    def guess_id(
        self,
        metasource,
        show_name,
        year,
        media_type
    ):
        print("Showname: '{}'".format(show_name)) if debug else ""
        ext_id = None

        matches = metasource.search(
            show_name, year=year, media_type=media_type
        )
        if len(matches) == 0:
            matches = metasource.search(
                show_name, year=None, media_type=media_type
            )

        ext_id = matches[0][0] if len(matches) == 1 else None

        if ext_id is None and len(matches) > 0 and year is not None:

            year_matches = Identifier.filter_by_year(matches, year)
            match_count = len(year_matches)

            matches = year_matches if match_count > 0 else matches

            ext_id = matches[0][0] if match_count == 1 else None

        if ext_id is None and len(matches) > 0:

            exact_matches = Identifier.filter_by_exact_match(
                matches,
                show_name,
                year
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
                print("Selecting 1st:", tuple(unique_matches[0]))
                for unique_match in unique_matches:
                    print(tuple(unique_match))
                print("")
                ext_id = matches[0][0]

        return ext_id

    @staticmethod
    def compile_re_search(show_name, exact_match, year):
        re_search_str = show_name
        re_search_str = re.sub(r'[^A-Za-z]+', ".+", re_search_str)
        re_search_str = re_search_str.strip('.+')

        if year:
            re_search_str = fr'{re_search_str}.+\({year}\)'

        if exact_match:
            re_search_str = "^" + re_search_str + "$"
        else:
            re_search_str = "(?:^|.*)" + re_search_str + "(?:.*|$)"

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
    def filter_by_exact_match(matches, show_name, year):
        print("Looking for exact matches:") if debug else ""

        re_search = Identifier.compile_re_search(
            show_name,
            exact_match=True,
            year=year
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
