class MetaSource(object):
    TV_SHOW = "TV_SHOW"
    MOVIE = "MOVIE"

    # [(id, title, year, media_type),]
    def search(title, year=None, media_type=None):
        pass

    # models.Meta
    def get_meta(ext_id):
        pass

    def sources():
        from metafinder.anidb import AniDB
        from metafinder.omdb import OMDB
        return (OMDB, AniDB)
