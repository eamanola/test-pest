from metafinder.metasource import MetaSource


class OMDB(MetaSource):
    KEY = "omdb"
    TV_SHOW = "series"
    MOVIE = "movie"

    META_ID_PREFIX = IMAGE_PREFIX = KEY

    def _clean_name(title):
        import re
        search_str = re.sub(r'[0-9]{4}', ".+", title)
        search_str = re.sub(r'[^0-9A-Za-z\']+', ".+", search_str).strip('.+')

        return search_str

    def search(title, year=None, media_type=None):
        import http.client
        import urllib

        TEST = False

        search_str = OMDB._clean_name(title)

        if TEST:
            data = TEST_SEARCH_RESPONCE
        else:
            params = {
                "apikey": "3bcf5854",
                "s": search_str,
                "r": "json",
            }
            if media_type:
                params["type"] = media_type
            if year:
                params["y"] = year
            print(params)

            try:
                conn = http.client.HTTPConnection("www.omdbapi.com")
                conn.request("GET", '/?' + urllib.parse.urlencode(params))

                response = conn.getresponse()
                data = response.read()
            finally:
                conn.close()

        return OMDB._parse_search(data)

    def _parse_search(data):
        ret = []

        import json
        data_obj = json.loads(data)
        print(data_obj)

        if data_obj['Response'] == 'False':
            print('not found')
            return []

        if "Search" in data_obj.keys():
            for result in data_obj['Search']:
                ret.append((
                    result['imdbID'],
                    result['Title'],
                    result['Year'],
                    result['Type']
                ))

        return ret

    def get_meta(ext_id):
        import http.client
        import urllib

        TEST = False

        if TEST:
            data = TEST_META_RESPONSE
        else:
            params = {
                "apikey": "3bcf5854",
                "i": ext_id,
                "r": "json",
                "plot": "short"
            }

            try:
                conn = http.client.HTTPConnection("www.omdbapi.com")
                conn.request("GET", '/?' + urllib.parse.urlencode(params))

                response = conn.getresponse()
                data = response.read()
            finally:
                conn.close()

        return OMDB._parse_meta(data)

    def _parse_meta(data):
        from models.meta import Meta
        id = None
        title = None
        rating = None
        image_name = None
        episodes = []
        description = None

        import json
        data_obj = json.loads(data)
        print(data_obj)

        if "Title" in data_obj.keys() and data_obj["Title"] != 'N/A':
            title = data_obj["Title"]

        if "imdbRating" in data_obj.keys() and data_obj["imdbRating"] != 'N/A':
            rating = data_obj["imdbRating"]

        if "Poster" in data_obj.keys() and data_obj["Poster"] != 'N/A':
            url = data_obj["Poster"]
            image_name = f'{OMDB.IMAGE_PREFIX}{data_obj["imdbID"]}{url[-4:]}'

            try:
                from api.images import Images
                Images.download_poster(url, image_name)
            except Exception:
                image_name = None

        if "Plot" in data_obj.keys() and data_obj["Plot"] != 'N/A':
            description = data_obj["Plot"]

        return Meta(
            f"{OMDB.META_ID_PREFIX}:::{data_obj['imdbID']}",
            title,
            rating,
            image_name,
            episodes,
            description
        )


TEST_SEARCH_RESPONCE = ''.join([
    '{"Search":[{"Title":"The Big Bang Theory","Year":"2007–2019"',
    ',"imdbID":"tt0898266","Type":"series","Poster":"https://m.me',
    'dia-amazon.com/images/M/MV5BY2FmZTY5YTktOWRlYy00NmIyLWE0ZmQt',
    'ZDg2YjlmMzczZDZiXkEyXkFqcGdeQXVyNjg4NzAyOTA@._V1_SX300.jpg"}',
    ',{"Title":"The Big Bang Theory After Show","Year":"2015–","i',
    'mdbID":"tt5612894","Type":"series","Poster":"N/A"}],"totalRe',
    'sults":"2","Response":"True"}'
    ])

TEST_META_RESPONSE = ''.join([
    '{"Title":"Love, Death & Robots","Year":"2019\xe2\x80\x93","R',
    'ated":"TV-MA","Released":"15 Mar 2019","Runtime":"15 min","G',
    'enre":"Animation, Short, Comedy, Fantasy, Horror, Sci-Fi","D',
    'irector":"N/A","Writer":"Tim Miller","Actors":"Scott Whyte, ',
    'Nolan North, Matthew Yang King, Chris Cox","Plot":"A collect',
    'ion of animated short stories that span various genres inclu',
    'ding science fiction, fantasy, horror and comedy.","Language',
    '":"English","Country":"USA","Awards":"Won 5 Primetime Emmys.',
    ' Another 4 wins & 5 nominations.","Poster":"https://m.media-',
    'amazon.com/images/M/MV5BMTc1MjIyNDI3Nl5BMl5BanBnXkFtZTgwMjQ1',
    'OTI0NzM@._V1_SX300.jpg","Ratings":[{"Source":"Internet Movie',
    ' Database","Value":"8.5/10"}],"Metascore":"N/A","imdbRating"',
    ':"8.5","imdbVotes":"90,736","imdbID":"tt9561862","Type":"ser',
    'ies","totalSeasons":"2","Response":"True"}'
])
