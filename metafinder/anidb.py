import re
from metafinder.metasource import MetaSource


class AniDB(MetaSource):
    KEY = "anidb"
    TV_SHOW = None
    MOVIE = None

    # From https://wiki.anidb.net/API#Data_Dumps
    DATA_DUMP_FILE_PATH = "./external/anidb-titles-nightly-20200913"
    DATABASE = "ani.db"
    TITLE_TO_ID_TABLE = "title_to_{}_id".format(KEY)
    META_ID_PREFIX = IMAGE_PREFIX = KEY

    def search(show_name, year, media_type=None):
        from metafinder.identifier import Identifier
        from db.db import get_db
        import sqlite3

        matches = None

        re_search = Identifier.compile_re_search(
            show_name,
            exact_match=False,
            year=year
        )
        try:
            db = get_db()
            db.connect(database=AniDB.DATABASE)

            try:
                matches = db.get_ext_ids(AniDB.TITLE_TO_ID_TABLE, re_search)
            except sqlite3.OperationalError:
                print('generating anidb table')

                AniDB._generate_search_table(db)
                matches = db.get_ext_ids(AniDB.TITLE_TO_ID_TABLE, re_search)

        finally:
            db.close()

        return matches

    def get_meta(anidb_id):
        TEST = False
        import os
        import sys
        import time
        META_FOLDER = os.path.join(sys.path[0], "meta")

        gzip = os.path.join(
            META_FOLDER, f'{AniDB.META_ID_PREFIX}_{anidb_id}.gz'
        )

        if (
            os.path.exists(gzip)
            and time.time() - int(os.path.getmtime(gzip)) < 24 * 60 * 60
        ):
            print('meta from file')
            with open(gzip, "rb") as f:
                meta = AniDB._parse(f.read())

        else:
            print('meta from server')
            if TEST:
                with open("data.gz", "rb") as f:
                    data = f.read()
            else:
                import http.client
                conn = http.client.HTTPConnection("api.anidb.net:9001")
                conn.request("GET", ''.join([
                    "/httpapi",
                    "?request=anime",
                    "&client=testpest",
                    "&clientver=1",
                    "&protover=1",
                    f"&aid={anidb_id}"
                ]))
                response = conn.getresponse()
                data = response.read()
                conn.close()

                time.sleep(3)  # avoid bann from anidb

            try:
                meta = AniDB._parse(data)
                from pathlib import Path
                Path(gzip).parent.mkdir(parents=True, exist_ok=True)

                with open(gzip, "wb") as f:
                    f.write(data)
            except Exception:
                meta = None

        return meta

    def _parse(data):
        import gzip
        import xml.etree.ElementTree
        from models.meta import Meta, Episode_Meta
        from api.images import Images

        uncompressed = gzip.decompress(data)
        root = xml.etree.ElementTree.fromstring(uncompressed)

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
        table = AniDB.TITLE_TO_ID_TABLE
        file_path = AniDB.DATA_DUMP_FILE_PATH
        results = AniDB._parse_data_dump_file(file_path)
        db.populate_title_to_ext_id_table(table, results)

    def _parse_data_dump_file(file_path):
        results = []

        try:
            file = open(file_path, "r")
            line = file.readline()

            while line:
                title = AniDB._parse_title_from_line(line)
                ext_id = AniDB._parse_id_from_line(line)
                year = AniDB._parse_year_from_line(line)
                media_type = AniDB._parse_media_type_from_line(line)

                result = (
                    ext_id if ext_id else "",
                    title if title else "",
                    year if year else 0,
                    media_type if media_type else ""
                )

                results.append(result)

                line = file.readline()

        finally:
            file.close()

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
