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
    def get_meta_getter(anidb_id):
        return AniDB_Meta_Getter(anidb_id)


class AniDB_Meta_Getter(Ext_Meta_Getter):
    IMAGE_PREFIX = AniDB.KEY
    META_ID_PREFIX = AniDB.KEY

    def __init__(self, anidb_id):
        super(AniDB_Meta_Getter, self).__init__(anidb_id)
        self._api_host = "api.anidb.net:9001"
        self._api_path = ''.join([
            "/httpapi",
            "?request=anime",
            "&client=testpest",
            "&clientver=1",
            "&protover=1",
            f"&aid={anidb_id}"
            ])
        self._meta_id = f"{AniDB_Meta_Getter.META_ID_PREFIX}:::{anidb_id}"

    def parse(self, data):
        import gzip
        import xml.etree.ElementTree
        from classes.meta import Meta

        uncompressed = gzip.decompress(data)
        root = xml.etree.ElementTree.fromstring(uncompressed)

        title = root.findall('./titles/title[@type="main"]')[0].text

        episodes = []
        _episodes = root.findall("./episodes/episode/epno[@type = '1']/..")
        namespace = "http://www.w3.org/XML/1998/namespace"
        for episode in _episodes:
            episodes.append((
                int(episode.find('./epno').text),
                episode.find(f'./title[@{{{namespace}}}lang="en"]').text
            ))

        temp_rating = float(root.find('./ratings/temporary').text)
        perm_rating = float(root.find('./ratings/permanent').text)
        rating = temp_rating if temp_rating > perm_rating else perm_rating

        _image_name = root.find("./picture").text
        image_host = 'cdn.anidb.net'
        image_path = f'/images/main/{_image_name}'
        image_name = AniDB_Meta_Getter.IMAGE_PREFIX + _image_name
        filename = 'anib'
        self.download_image(
            image_host,
            image_path,
            image_name
        )

        description = root.find("./description").text.replace("\n", " ")
        return Meta(
            self._meta_id,
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
