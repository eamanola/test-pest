import re
from metafinder.metasource import MetaSource


class AniDB(MetaSource):
    KEY = "anidb"
    TV_SHOW = None
    MOVIE = None

    DATABASE = "ani.db"
    TITLE_TO_ID_TABLE = "title_to_{}_id".format(KEY)
    META_ID_PREFIX = IMAGE_PREFIX = KEY

    def _clean_name(title, year):
        import re
        re_search_str = title
        re_search_str = re.sub(r'[^A-Za-z]+', ".+", re_search_str)
        re_search_str = re_search_str.strip('.+')

        if year:
            re_search_str = fr'{re_search_str}.+\({year}\)'

        re_search_str = "(?:^|.*)" + re_search_str + "(?:.*|$)"

        return re.compile(re_search_str, re.IGNORECASE)

    def search(show_name, year, media_type=None):
        from metafinder.identifier import Identifier
        from db.db import get_db
        import sqlite3

        matches = None

        re_search = AniDB._clean_name(show_name, year)
        try:
            db = get_db()
            db.connect(database=AniDB.DATABASE)

            try:
                matches = db.get_ext_ids(AniDB.TITLE_TO_ID_TABLE, re_search)
            except sqlite3.OperationalError:
                print('generating anidb table')

                AniDB._generate_search_table(db)
                matches = db.get_ext_ids(AniDB.TITLE_TO_ID_TABLE, re_search)

            if len(matches) == 0 and year is not None:
                re_search = AniDB._clean_name(show_name, None)
                matches = db.get_ext_ids(AniDB.TITLE_TO_ID_TABLE, re_search)

        finally:
            db.close()

        return matches

    def get_meta(anidb_id):
        TEST = False
        import os
        import sys
        import time

        from metafinder.metacache import MetaCache

        data = MetaCache.load(f'{AniDB.META_ID_PREFIX}_{anidb_id}')
        if data is None:
            import gzip
            print('meta from server')
            if TEST:
                with gzip.open("data.gz", "rb") as f:
                    data = f.read()
            else:
                import http.client
                try:
                    conn = http.client.HTTPConnection("api.anidb.net:9001")
                    conn.request("GET", ''.join([
                        "/httpapi",
                        "?request=anime",
                        "&client=testpest",
                        "&clientver=1",
                        "&protover=1",
                        f"&aid={anidb_id}"
                    ]))
                    data = gzip.decompress(conn.getresponse().read())
                finally:
                    conn.close()

                MetaCache.save(f'{AniDB.META_ID_PREFIX}_{anidb_id}', data)

                time.sleep(3)  # avoid bann from anidb

        try:
            meta = AniDB._parse(data)
        except Exception:
            meta = None

        return meta

    def _parse(data):
        import xml.etree.ElementTree
        from models.meta import Meta, Episode_Meta
        from api.images import Images

        root = xml.etree.ElementTree.fromstring(data)

        anidb_id = root.attrib['id']

        title = root.findall('./titles/title[@type="main"]')[0].text

        episodes = []
        _episodes = root.findall("./episodes/episode/epno[@type = '1']/..")
        namespace = "http://www.w3.org/XML/1998/namespace"
        for episode in _episodes:
            episode_data = []

            episode_num = int(episode.find('./epno').text)

            episode_summary = ""
            summary = episode.find('./summary')
            if summary is not None:
                episode_summary = summary.text

            episode_title = episode.find(
                f'./title[@{{{namespace}}}lang="en"]'
            ).text

            episodes.append(Episode_Meta(
                episode_num,
                -1,
                episode_title,
                episode_summary
            ))

        temp_rating = float(root.find('./ratings/temporary').text)
        perm_rating = float(root.find('./ratings/permanent').text)
        rating = temp_rating if temp_rating > perm_rating else perm_rating

        _image_name = root.find("./picture").text
        image_url = f'http://cdn.anidb.net/images/main/{_image_name}'

        image_name = AniDB.IMAGE_PREFIX + _image_name
        Images.download_poster(image_url, image_name)

        description_node = root.find("./description")
        if description_node is not None:
            description = description_node.text.replace("\n", " ")
        else:
            description = ""

        return Meta(
            f"{AniDB.META_ID_PREFIX}:::{anidb_id}",
            title,
            rating,
            image_name,
            episodes,
            description
        )

    def _generate_search_table(db):
        TEST = False
        # download latest anime-titles.dat here:
        # From https://wiki.anidb.net/API#Data_Dumps
        import os
        import sys

        ANIME_TITLES_DAT = os.path.join(sys.path[0], "anime-titles.dat.gz")
        if not os.path.exists(ANIME_TITLES_DAT):
            data = None

            if TEST:
                with open('anime-titles-test.dat.gz', "rb") as f:
                    data = f.read()
            else:
                import http.client
                try:
                    # From https://wiki.anidb.net/API#Data_Dumps
                    conn = http.client.HTTPSConnection("anidb.net")
                    conn.request(
                        "GET",
                        '/api/anime-titles.dat.gz',
                        headers={"User-Agent": "testpest/1.0"}
                    )

                    data = conn.getresponse().read()
                finally:
                    conn.close()

            if data:
                os.makedirs(os.path.dirname(ANIME_TITLES_DAT), exist_ok=True)
                with open(ANIME_TITLES_DAT, "wb") as f:
                    f.write(data)

                file_path = ANIME_TITLES_DAT
        else:
            file_path = ANIME_TITLES_DAT

        results = AniDB._parse_data_dump_file(file_path)
        table = AniDB.TITLE_TO_ID_TABLE
        db.populate_title_to_ext_id_table(table, results)

    def _parse_data_dump_file(file_path):
        results = []

        import gzip
        with gzip.open(file_path, "r") as file:
            line = file.readline().decode("utf-8")

            while line:
                title = AniDB._parse_title_from_line(line)
                ext_id = AniDB._parse_id_from_line(line)
                year = AniDB._parse_year_from_line(line)
                media_type = AniDB._parse_media_type_from_line(line)
                del line

                result = (
                    ext_id if ext_id else "",
                    title if title else "",
                    year if year else 0,
                    media_type if media_type else ""
                )

                results.append(result)

                line = file.readline().decode("utf-8")


        return results

    def _parse_title_from_line(line):
        parts = line.strip().split("|")
        return parts[len(parts) - 1]

    def _parse_id_from_line(line):
        parts = line.strip().split("|")
        return parts[0]

    def _parse_year_from_line(line):
        title = AniDB._parse_title_from_line(line)
        year_re = re.compile(r'.*\((\d{4})\).*')
        year_group = year_re.match(title)
        if year_group:
            year = int(year_group.group(1))
        else:
            year = None

        return year

    def _parse_media_type_from_line(line):
        return None
