import re
import sys
import os
sys.path.append(os.path.join(sys.path[0], '..'))
from classes.db import DB

debug = True;
debug = False;

class Identifier(object):
    TV_SHOW = "TV_SHOW";
    MOVIE = "MOVIE"

    def __init__(self):
        super(Identifier, self).__init__()

    def get_ext_ids(self, re_search):
        raise NotImplementedError()

    @staticmethod
    def compile_re_search(show_name: str, exact_match: bool):
        re_search_str = show_name;

        re_search_str = re.sub('[^a-zA-Z]s\s*\d+(?:[^a-zA-Z]|$)', "", re_search_str, flags=re.IGNORECASE)
        re_search_str = re.sub('[^a-zA-Z]part[^a-zA-Z]', "", re_search_str, flags=re.IGNORECASE)
        re_search_str = re.sub('[^a-zA-Z]ova(?:[^a-zA-Z]|$)', "", re_search_str, flags=re.IGNORECASE)
        re_search_str = re.sub('(?:season)+s?', "", re_search_str, flags=re.IGNORECASE)
        re_search_str = re.sub('[^A-Za-z]+', ".+", re_search_str)
        re_search_str = re.sub('^\.(?:\*|\+)', "", re_search_str)
        re_search_str = re.sub('\.(?:\*|\+)$', "", re_search_str)

        if exact_match:
            re_search_str = "^" + re_search_str + "$"
        else:
            re_search_str = ".*" + re_search_str + ".*"

        return re.compile(re_search_str, re.IGNORECASE);

    @staticmethod
    def print_result(matches):
        match_count = len(matches);

        if match_count == 0:
            result_str = "No matches found."
        elif match_count == 1:
            result_str = "Single match: {}".format(matches[0])
        else:
            result_str = "{} matches found.".format(match_count)

        print(result_str);

        line = ""
        for _ in range(len(result_str)):
            line = line + "-"
        print(line)

        print("");

    def search_db(self, show_name):
        re_search = Identifier.compile_re_search(show_name, exact_match = False)
        print('Searching for:', re_search) if debug else "";

        matches = self.get_ext_ids(re_search);

        Identifier.print_result(matches) if debug else ""

        return matches;

    def filter_by_year(self, matches, year):
        print("Filtering by year:") if debug else "";

        year_matches = []
        for match in matches:
            print('*', match) if debug else "";
            if year == match[2]:
                print('--year match.') if debug else "";
                year_matches.append(match);

        Identifier.print_result(year_matches) if debug else ""

        return year_matches;

    def filter_by_exact_match(self, matches, show_name):
        print("Looking for exact matches:") if debug else "";

        re_search = Identifier.compile_re_search(show_name, exact_match = True);
        print('Searching for:', re_search) if debug else "";

        exact_matches = []
        for match in matches:
            print('*', match) if debug else "";
            title = match[1];
            if re_search.match(title):
                print('--exact match.') if debug else "";
                exact_matches.append(match);

        Identifier.print_result(exact_matches) if debug else ""

        return exact_matches;

    def filter_by_media_type(self, matches, media_type):
        print("Filtering by media type:") if debug else "";

        media_type_matches = []
        for match in matches:
            print('*', match) if debug else "";
            match_media_type = match[3];
            if match_media_type and media_type == match_media_type:
                print('--media type match.') if debug else "";
                media_type_matches.append(match);

        Identifier.print_result(media_type_matches) if debug else ""

        return media_type_matches;

    def group_by_id(self, matches):
        print("Grouping by ids:") if debug else "";

        unique_matches = [];
        for match in matches:
            print('*', match) if debug else "";
            ani_id = match[0]
            found = False;
            for unique_match in unique_matches:
                if(unique_match[0] == ani_id):
                    found = True;
                    break;
            if found == False:
                print('--unique match.') if debug else "";
                unique_matches.append(match);

        Identifier.print_result(unique_matches) if debug else ""
        return unique_matches;

    def guess_id(
    self,
    show_name,
    year,
    media_type):
        print("Showname: '{}'".format(show_name)) if debug else "";
        ext_id = None;

        matches = self.search_db(show_name)

        ext_id = matches[0][0] if len(matches) == 1 else None;

        if ext_id == None and len(matches) > 0 and year != None:

            year_matches = self.filter_by_year(matches, year);
            match_count = len(year_matches);

            matches = year_matches if match_count > 0 else matches;

            ext_id = matches[0][0] if match_count == 1 else None;

        if ext_id == None and len(matches) > 0:

            exact_matches = self.filter_by_exact_match(matches, show_name);
            match_count = len(exact_matches);

            matches = exact_matches if match_count > 0 else matches;

            ext_id = matches[0][0] if match_count == 1 else None;

        if ext_id == None and len(matches) > 0 and media_type != None:

            media_type_matches = self.filter_by_media_type(matches, media_type);
            match_count = len(media_type_matches);

            matches = media_type_matches if match_count > 0 else matches;

            ext_id = matches[0][0] if match_count == 1 else None;

        if ext_id == None and len(matches) > 0:

            unique_matches = self.group_by_id(matches);
            match_count = len(unique_matches);

            matches = unique_matches if match_count > 0 else matches;

            ext_id = matches[0][0] if match_count == 1 else None;

            if match_count > 1: ## TODO: more filters?
                print(match_count, "unique matches for:", show_name) #if debug else "";
                print("Selecting 1st:", unique_matches[0]) #if debug else "";
                for unique_match in unique_matches:
                    print(unique_match)
                print("");
                ext_id = matches[0][0];

        return ext_id;

class AniDBIdentifier(Identifier):
    TV_SHOW = None;
    MOVIE = None

    def __init__(self):
        super(AniDBIdentifier, self).__init__()

    def get_ext_ids(self, re_search):
        db = DB.get_instance();
        db.connect();

        matches = db.get_anidb_ids(re_search);

        db.close()

        return matches;

class IMDBIdentifier(Identifier):
    TV_SHOW = "tvEpisode";
    MOVIE = "movie"

    def __init__(self):
        super(IMDBIdentifier, self).__init__()

    def get_ext_ids(self, re_search):
        db = DB.get_instance();
        db.connect();

        matches = db.get_imdb_ids(re_search);

        db.close()

        return matches;

#print(IMDBIdentifier().guess_id("The Intouchables", 2011))
#print(IMDBIdentifier().guess_id("Mulan", 2020, 'movie'))
#print("tt0000001	short	Carmencita	Carmencita	0	1894	\N	1	Documentary,Short")

#print(AniDBIdentifier().guess_id("JoJo's Bizarre Adventure - OVA (2000)", 2000, 'foo'));
#print(guess_id("JoJo's Bizarre Adventure - OVA (2000)"));
