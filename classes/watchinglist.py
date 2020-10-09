from classes.container import MediaLibrary, Show, Season, Extra
from classes.media import Episode
from classes.db import DB


class WatchingList(object):

    def __init__(self):
        super(WatchingList, self).__init__()

    @staticmethod
    def started_play(db, media):
        episodes = [m for m in media if isinstance(m, Episode)]

        shows = []
        for e in episodes:
            show = e.parent()
            if show.__class__.__name__ != "Show":
                show = db.get_container(e.parent()).parent()

            shows.append(show)

        db.create_watchlist_table()

        new_show_ids = []
        for s in shows:
            if (
                not s.id() in new_show_ids and
                not db.is_in_watchlists(s.id())
            ):
                new_show_ids.append(s.id())
                print(s.title(), 'added to watchlist')
            else:
                print(s.title(), 'already in watchlist')

        db.add_to_watchlist(new_show_ids)

        return None

    @staticmethod
    def get_play_next_list(db):
        db.create_watchlist_table()
        shows = db.get_watchlist()
        remove = []
        play_next = []
        for show in shows:
            media = None
            if len(show.media) > 0:
                media = WatchingList.get_next_media(show)

            if media is None and len(show.containers) > 0:
                media = WatchingList.get_next_container(db, show)

            if media is None:
                print('Nothing found for', show.title())
                print('removing', show.title())
                remove.append(show.id())
            else:
                play_next.append(media)

        if len(remove) > 0:
            db.remove_from_watchlist(remove)

        return play_next

    @staticmethod
    def get_next_media(container):
        list = sorted(
            [m for m in container.media if not m.played()],
            key=lambda med: med.title()
        )

        return list[0] if len(list) else None

    @staticmethod
    def get_next_container(db, show):
        seasons = sorted(
            [c for c in show.containers if c.__class__.__name__ == "Season"],
            key=lambda season: season.season_number()
        )

        media = None
        for season in seasons:
            media = WatchingList.get_next_media(db.get_container(season))
            if media:
                break

        return media
