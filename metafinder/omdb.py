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
        import json

        TEST = False

        search_str = OMDB._clean_name(title)

        if TEST:
            data = TEST_SEARCH_RESPONSE
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
            # print(params)

            try:
                conn = http.client.HTTPConnection("www.omdbapi.com")
                conn.request("GET", '/?' + urllib.parse.urlencode(params))

                data = conn.getresponse().read()

                result = json.loads(data)
                if (
                    "y" in params
                    and (
                        "Search" not in result.keys()
                        or len(result["Search"]) == 0
                    )
                ):
                    del params["y"]
                    conn.request("GET", '/?' + urllib.parse.urlencode(params))

                    data = conn.getresponse().read()
            finally:
                conn.close()

        return OMDB._parse_search(data)

    def _parse_search(data):
        ret = []

        import json
        data_obj = json.loads(data)
        # print(data_obj)

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
        TEST = False

        if TEST:
            data = TEST_META_RESPONSE
        else:
            from metafinder.metacache import MetaCache

            data = MetaCache.load(f'{OMDB.META_ID_PREFIX}_{ext_id}')

            if data is None:
                import http.client
                import urllib

                print('meta from server')

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

                MetaCache.save(f'{OMDB.META_ID_PREFIX}_{ext_id}', data)

        meta = OMDB._parse_meta(data)

        episode_meta = OMDB._get_episodes(data)
        for em in episode_meta:
            meta.episodes().append(em)

        return meta

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
        # print(data_obj)

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

    def _get_episodes(show_meta_data):
        import json

        show_meta = json.loads(show_meta_data)

        if "imdbID" not in show_meta.keys():
            print('OMDB._get_episodes: No id')
            return []

        if (
            "Type" not in show_meta.keys()
            or show_meta["Type"] != OMDB.TV_SHOW
        ):
            print('OMDB._get_episodes: Not a show')
            return []

        if (
            "totalSeasons" not in show_meta.keys()
            or show_meta["totalSeasons"] == 'N/A'
            or int(show_meta["totalSeasons"]) <= 0
        ):
            print('OMDB._get_episodes: no season info')
            return []

        seasons_meta_data = []
        seasons = range(1, int(show_meta["totalSeasons"]) + 1)

        TEST = False

        if TEST:
            seasons_meta_data.append(TEST_SEASON_RESPONSE)

        else:
            from metafinder.metacache import MetaCache

            ext_id = show_meta["imdbID"]
            data = MetaCache.load(f'{OMDB.META_ID_PREFIX}_{ext_id}_seasons')

            if data:
                print('Seasons from file')
                seasons_meta_data = json.loads(data)
            else:
                import time
                import http.client
                import urllib

                print('Seasons from server')

                params = {
                    "apikey": "3bcf5854",
                    "i": ext_id,
                    "r": "json"
                }

                try:
                    conn = http.client.HTTPConnection("www.omdbapi.com")

                    for s in seasons:
                        conn.request("GET", '/?' + urllib.parse.urlencode(
                            {**params, "Season": s}
                        ))
                        seasons_meta_data.append(json.loads(
                            conn.getresponse().read()
                        ))
                        # print(seasons_meta_data[-1])
                        time.sleep(1)
                finally:
                    conn.close()

                MetaCache.save(
                    f'{OMDB.META_ID_PREFIX}_{ext_id}_seasons',
                    bytes(json.dumps(seasons_meta_data), "utf8")
                )

        return OMDB._parse_episodes(seasons_meta_data)

    def _parse_episodes(seasons_meta):
        from models.meta import Episode_Meta

        meta_episodes = []

        for season_meta in seasons_meta:

            if season_meta["Response"] == "False":
                continue

            season_number = int(season_meta["Season"])

            for episode in season_meta["Episodes"]:
                meta_episodes.append(
                    Episode_Meta(
                        int(episode["Episode"]),
                        season_number,
                        episode["Title"],
                        ""
                    )
                )

        return meta_episodes


TEST_SEARCH_RESPONSE = ''.join([
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

TEST_SEASON_RESPONSE = ''.join([
    '{"Title":"Love, Death & Robots","Season":"1","totalSeasons":"',
    '2","Episodes":[{"Title":"Sonnie\'s Edge","Released":"2019-03-',
    '15","Episode":"1","imdbRating":"8.3","imdbID":"tt9781722"},{"',
    'Title":"Suits","Released":"2019-03-15","Episode":"4","imdbRat',
    'ing":"7.8","imdbID":"tt9788490"},{"Title":"Sucker of Souls","',
    'Released":"2019-03-15","Episode":"5","imdbRating":"6.5","imdb',
    'ID":"tt9788492"},{"Title":"When the Yogurt Took Over","Releas',
    'ed":"2019-03-15","Episode":"6","imdbRating":"6.9","imdbID":"t',
    't9788494"},{"Title":"Beyond the Aquila Rift","Released":"2019',
    '-03-15","Episode":"7","imdbRating":"8.6","imdbID":"tt9788496"',
    '},{"Title":"The Dump","Released":"2019-03-15","Episode":"9","',
    'imdbRating":"6.3","imdbID":"tt9788500"},{"Title":"Shape-Shift',
    'ers","Released":"2019-03-15","Episode":"10","imdbRating":"7.5',
    '","imdbID":"tt9788502"},{"Title":"Helping Hand","Released":"',
    '2019-03-15","Episode":"11","imdbRating":"7.7","imdbID":"tt978',
    '8504"},{"Title":"Fish Night","Released":"2019-03-15","Episode',
    '":"12","imdbRating":"6.4","imdbID":"tt9788506"},{"Title":"Luc',
    'ky 13","Released":"2019-03-15","Episode":"13","imdbRating":"8',
    '.0","imdbID":"tt9788508"},{"Title":"Zima Blue","Released":"20',
    '19-03-15","Episode":"14","imdbRating":"8.3","imdbID":"tt97885',
    '10"},{"Title":"Blind Spot","Released":"2019-03-15","Episode":',
    '"15","imdbRating":"6.4","imdbID":"tt9788512"},{"Title":"Ice A',
    'ge","Released":"2019-03-15","Episode":"16","imdbRating":"7.4"',
    ',"imdbID":"tt9788514"},{"Title":"Alternate Histories","Releas',
    'ed":"2019-03-15","Episode":"17","imdbRating":"6.4","imdbID":"',
    'tt9788516"},{"Title":"The Secret War","Released":"2019-03-15"',
    ',"Episode":"18","imdbRating":"8.1","imdbID":"tt9788518"}],"Re',
    'sponse":"True"}'
])
