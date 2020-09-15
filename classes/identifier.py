import re

debug = True;
debug = False;

class Identifier(object):
    TV_SHOW = "TV_SHOW";
    MOVIE = "MOVIE"

    def __init__(self):
        super(Identifier, self).__init__()
        self.ID_TITLES_FILE_PATH = None;

    @staticmethod
    def parse_title_from_line(line):
        raise NotImplementedError();
    @staticmethod
    def parse_id_from_line(line):
        raise NotImplementedError();
    @staticmethod
    def parse_year_from_line(line):
        raise NotImplementedError();
    @staticmethod
    def parse_media_type_from_line(line):
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

    def search_file(self, show_name):
        re_search = Identifier.compile_re_search(show_name, exact_match = False)
        print('Searching for:', re_search) if debug else "";

        matches = [];

        ext_titles = open(self.ID_TITLES_FILE_PATH, "r");
        line = ext_titles.readline();

        while line:
            title = self.parse_title_from_line(line);
            if re_search.match(title):
                matches.append(line.strip());

            line = ext_titles.readline();

        ext_titles.close();

        Identifier.print_result(matches) if debug else ""

        return matches;

    def filter_by_year(self, matches, year):
        print("Filtering by year:") if debug else "";

        year_matches = []
        for match in matches:
            print('*', match) if debug else "";
            match_year = self.parse_year_from_line(match);
            if year == match_year:
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
            title = self.parse_title_from_line(match);
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
            match_media_type = self.parse_media_type_from_line(match);
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
            ani_id = self.parse_id_from_line(match);
            found = False;
            for unique_match in unique_matches:
                if(unique_match.startswith(ani_id)):
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

        matches = self.search_file(show_name);
        ext_id = self.parse_id_from_line(matches[0]) if len(matches) == 1 else None;

        if ext_id == None and len(matches) > 0 and year != None:

            year_matches = self.filter_by_year(matches, year);
            match_count = len(year_matches);

            matches = year_matches if match_count > 0 else matches;

            ext_id = self.parse_id_from_line(matches[0]) if match_count == 1 else None;

        if ext_id == None and len(matches) > 0:

            exact_matches = self.filter_by_exact_match(matches, show_name);
            match_count = len(exact_matches);

            matches = exact_matches if match_count > 0 else matches;

            ext_id = self.parse_id_from_line(matches[0]) if match_count == 1 else None;

        if ext_id == None and len(matches) > 0 and media_type != None:

            media_type_matches = self.filter_by_media_type(matches, media_type);
            match_count = len(media_type_matches);

            matches = media_type_matches if match_count > 0 else matches;

            ext_id = self.parse_id_from_line(matches[0]) if match_count == 1 else None;

        if ext_id == None and len(matches) > 0:


            unique_matches = self.group_by_id(matches);
            match_count = len(unique_matches);

            matches = unique_matches if match_count > 0 else matches;

            ext_id = self.parse_id_from_line(matches[0]) if match_count == 1 else None;

            if match_count > 1: ## TODO: more filters?
                print(match_count, "unique matches for:", show_name) #if debug else "";
                print("Selecting 1st:", unique_matches[0]) #if debug else "";
                print(unique_matches)
                ext_id = self.parse_id_from_line(unique_matches[0]);

        return ext_id;

class AniDBIdentifier(Identifier):
    TV_SHOW = None;
    MOVIE = None

    def __init__(self):
        super(AniDBIdentifier, self).__init__()
        #latest available at https://wiki.anidb.net/API#Data_Dumps
        self.ID_TITLES_FILE_PATH = "./external/anidb-titles-nightly-20200913"

    @staticmethod
    def parse_title_from_line(line):
        parts = line.strip().split("|");
        return parts[len(parts) - 1];

    @staticmethod
    def parse_id_from_line(line):
        parts = line.strip().split("|");
        return parts[0];

    @staticmethod
    def parse_year_from_line(line):
        title = AniDBIdentifier.parse_title_from_line(line);
        year_re = re.compile('.*\((\d{4})\).*');
        year_group = year_re.match(title);
        if year_group:
            year = int(year_group.group(1));
        else:
            year = None;

        return year;

    @staticmethod
    def parse_media_type_from_line(line):
        return None;

    def guess_id(self, show_name, year, media_type):

        #not supported in titles file
        media_type = None;

        return super().guess_id(
        show_name,
        year,
        media_type);

class IMDBIdentifier(Identifier):
    TV_SHOW = "tvEpisode";
    MOVIE = "movie"

    def __init__(self):
        super(IMDBIdentifier, self).__init__()
        #latest available at https://datasets.imdbws.com/
        self.ID_TITLES_FILE_PATH = "./external/imdb-titles-nightly-20200913"

    @staticmethod
    def parse_title_from_line(line):
        parts = line.strip().split("\t");
        return parts[2];

    @staticmethod
    def parse_id_from_line(line):
        parts = line.strip().split("\t");
        return parts[0];

    @staticmethod
    def parse_year_from_line(line):
        parts = line.strip().split("\t");

        if re.compile('^\d{4}$').match(parts[5]):
            year = int(parts[5]);
        else:
             year = None;

        return year;

    @staticmethod
    def parse_media_type_from_line(line):
        parts = line.strip().split("\t");
        return parts[1];

    def guess_id(self, show_name, year, media_type):
        return super().guess_id(
        show_name,
        year,
        media_type);

#print(IMDBIdentifier().guess_id("The Intouchables", 2011))
#print(IMDBIdentifier().guess_id("Mulan", 2020, 'movie'))
#print("tt0000001	short	Carmencita	Carmencita	0	1894	\N	1	Documentary,Short")

#print(AniDBIdentifier().parse_year_from_line_anidb("789|1|x-jat|JoJo no Kimyou na Bouken (2000)"));
#print(AniDBIdentifier().guess_id("JoJo's Bizarre Adventure - OVA (2000)", 2000, 'foo'));
#print(guess_id("JoJo's Bizarre Adventure - OVA (2000)"));
