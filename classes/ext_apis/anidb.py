import re
from classes.ext_api import Ext_api
from classes.ext_title_to_id_file_parser import Ext_title_to_id_file_parser
from classes.ext_meta_getter import Ext_Meta_Getter


class AniDB(Ext_api):
    KEY = "anidb"
    TV_SHOW = None
    MOVIE = None
    TITLE_TO_ID_TABLE = "title_to_{}_id".format(KEY)
    # From https://wiki.anidb.net/API#Data_Dumps
    TITLE_TO_ID_FILE_PATH = "./external/anidb-titles-nightly-20200913"

    title_to_id_file_parser = None

    def __init__(self):
        super(AniDB, self).__init__()

    @staticmethod
    def get_title_to_id_file_parser():
        if AniDB.title_to_id_file_parser is None:
            AniDB.title_to_id_file_parser = Anidb_title_to_id_file_parser()

        return AniDB.title_to_id_file_parser

    @staticmethod
    def get_meta_getter():
        return AniDB_Meta_Getter


class AniDB_Meta_Getter(Ext_Meta_Getter):
    IMAGE_PREFIX = META_ID_PREFIX = AniDB.KEY

    def __init__(self, anidb_id):
        super(AniDB_Meta_Getter, self).__init__(anidb_id)

    def get(anidb_id):
        TEST = False
        import os
        import sys
        import time
        META_FOLDER = os.path.join(sys.path[0], "meta")

        gzip = os.path.join(
            META_FOLDER, f'{AniDB_Meta_Getter.META_ID_PREFIX}_{anidb_id}.gz'
        )

        if (
            os.path.exists(gzip)
            and time.time() - int(os.path.getmtime(gzip)) < 24 * 60 * 60
        ):
            print('meta from file')
            with open(gzip, "rb") as f:
                meta = AniDB_Meta_Getter.parse(f.read())

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
                meta = AniDB_Meta_Getter.parse(data)

                from pathlib import Path
                Path(gzip).parent.mkdir(parents=True, exist_ok=True)

                with open(gzip, "wb") as f:
                    f.write(data)
            except Exception:
                meta = None

        return meta

    def parse(data):
        import gzip
        import xml.etree.ElementTree
        from classes.meta import Meta, Episode_Meta
        from classes.images import Images

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
                episode_title,
                episode_summary
            ))

        temp_rating = float(root.find('./ratings/temporary').text)
        perm_rating = float(root.find('./ratings/permanent').text)
        rating = temp_rating if temp_rating > perm_rating else perm_rating

        _image_name = root.find("./picture").text
        image_host = 'cdn.anidb.net'
        image_path = f'/images/main/{_image_name}'
        image_name = AniDB_Meta_Getter.IMAGE_PREFIX + _image_name
        Images.download_poster(image_host, image_path, image_name)

        description_node = root.find("./description")
        if description_node is not None:
            description = description_node.text.replace("\n", " ")
        else:
            description = ""

        return Meta(
            f"{AniDB_Meta_Getter.META_ID_PREFIX}:::{anidb_id}",
            title,
            rating,
            image_name,
            episodes,
            description
        )


class Anidb_title_to_id_file_parser(Ext_title_to_id_file_parser):
    def __init__(self):
        super(Anidb_title_to_id_file_parser, self).__init__()

    @staticmethod
    def parse_title_from_line(line):
        parts = line.strip().split("|")
        return parts[len(parts) - 1]

    @staticmethod
    def parse_id_from_line(line):
        parts = line.strip().split("|")
        return parts[0]

    @staticmethod
    def parse_year_from_line(line):
        title = Anidb_title_to_id_file_parser.parse_title_from_line(line)
        year_re = re.compile(r'.*\((\d{4})\).*')
        year_group = year_re.match(title)
        if year_group:
            year = int(year_group.group(1))
        else:
            year = None

        return year

    @staticmethod
    def parse_media_type_from_line(line):
        return None
