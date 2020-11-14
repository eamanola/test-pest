from classes.db import DB
from classes.container import Extra, Season, Show, MediaLibrary
from classes.media import Media, Movie, Episode
from classes.identifiable import Identifiable
from classes.watchinglist import WatchingList
from classes.ext_apis.anidb import AniDB


def get_container(db, container_id):
    container = db.get_container(container_id)

    if container:
        parent = container.parent()
        while parent and isinstance(parent, (Extra, Season, Show)):
            parent.set_parent(db.get_container(parent.parent()))
            parent = parent.parent()

        if (
            isinstance(container, (Extra, Season, Show))
            and (
                len(container.containers) == 1
                and len(container.media) == 0
            )
        ):
            _remove_singles = db.get_container(container.containers[0])
            print('skip', _remove_singles.title())
            while (
                _remove_singles
                and (
                    len(_remove_singles.containers) == 1
                    and len(_remove_singles.media) == 0
                )
            ):
                _remove_singles = db.get_container(
                    _remove_singles.containers[0]
                )
                print('skip', _remove_singles.title())

            if _remove_singles:
                container.containers.clear()
                container.media.clear()
                container.media = _remove_singles.media

        for c in container.containers:
            c.set_unplayed_count(db.get_unplayed_count(c.id()))

        container.set_unplayed_count(db.get_unplayed_count(container.id()))

    return container


def get_media(db, media_id):
    media = db.get_media(media_id)

    if media:
        if isinstance(media, Episode):
            media.set_parent(db.get_container(media.parent()))
            parent = media.parent()

            while parent and isinstance(parent, (Extra, Season, Show)):
                parent.set_parent(db.get_container(parent.parent()))
                parent = parent.parent()

    return media


def get_media_libraries(db):
    cur = db.conn.cursor()
    sql = 'select id from containers where type="MediaLibrary"'
    cur.execute(sql)
    return [result[0] for result in cur.fetchall()]


def play_next_list(db):
    play_next_list = WatchingList.get_play_next_list(db)

    for media in play_next_list:
        if isinstance(media, Episode):
            parent = media.parent()
            while parent and isinstance(parent, (Extra, Season, Show)):
                parent.set_parent(db.get_container(parent.parent()))
                parent = parent.parent()

    return play_next_list


def scan(db, container_id):
    from classes.scanner import Scanner

    scanned = None

    def collect_objs(con, containers=[], media=[]):
        containers = containers + con.containers
        media = media + con.media

        for container in con.containers:
            containers, media = collect_objs(container, containers, media)

        return containers, media

    container = db.get_container(container_id)
    if container:
        containers, media = collect_objs(container)
        containers.append(container)
        db.delete_containers(containers)
        db.delete_media(media)

        container.containers.clear()
        container.media.clear()

        result = None
        if isinstance(container, Extra):
            result = Scanner().scan_extra(container)
        elif isinstance(container, Season):
            result = Scanner().scan_season(container)
        elif isinstance(container, Show):
            result = Scanner().scan_show(container)
        elif isinstance(container, MediaLibrary):
            result = Scanner().scan_media_library(container)

        if result:
            containers, media = collect_objs(result)
            containers.append(result)

            db.create_containers_table()
            db.create_media_table()

            db.update_containers(
                containers,
                update_identifiables=False
            )
            db.update_media(
                media,
                update_identifiables=False,
                overwrite_media_states=False
            )

            scanned = result.id()

    return scanned


def _identify(db, identifiable, media_type):
    from classes.identifier import Identifier

    anidb_id = Identifier(AniDB).guess_id(
        db,
        identifiable.title(),
        identifiable.year(),
        media_type
    )

    return anidb_id


def container_identify(db, container_id):
    found, identified = False, False

    container = db.get_container(container_id)

    if container and isinstance(container, Identifiable):
        found = True

        anidb_id = _identify(db, container, AniDB.TV_SHOW)

        if anidb_id:
            container.ext_ids()[AniDB.KEY] = anidb_id
            db.update_containers([container])
            identified = True

    return found, identified


def media_identify(db, media_id):
    found, identified = False, False

    media = db.get_media(media_id)

    if media and isinstance(media, Identifiable):
        found = True
        anidb_id = _identify(db, media, AniDB.MOVIE)

        if anidb_id:
            media.ext_ids()[AniDB.KEY] = anidb_id
            db.update_media([media])
            identified = True

    return found, identified


def play(db, media_ids):
    import os
    import sys
    import subprocess

    media = []
    for media_id in media_ids:
        m = db.get_media(media_id)
        if m:
            media.append(m)

    if len(media) > 0:
        file_paths = [
            f'{os.path.join(m.parent().path(), m.file_path())}'
            for m in media
        ]

        cmd_vlc = [
            'vlc', '--fullscreen' #, '--mouse-hide-timeout 3000'
        ] + file_paths

        # cmd_mpv = ['mpv', '--fullscreen', '--slang=en,eng'] + file_paths

        # cmd_play = [os.path.join(sys.path[0], 'play.sh')] + file_paths

        cmd = cmd_vlc
        subprocess.Popen(cmd)

        WatchingList.started_play(db, media)


def media_played(db, media_id, played):
    found = False

    media = db.get_media(media_id)

    if media:
        found = True

        if media.played() != played:
            media.set_played(played)
            db.update_media([media])

    return found


def container_played(db, container_id, played):
    found = False
    container = db.get_container(container_id)

    if container:
        found = True
        db.set_played(container_id, played)

    return found


def _get_info(db, identifiable):
    info_updated = False

    if (
        identifiable and
        isinstance(identifiable, Identifiable) and
        AniDB.KEY in identifiable.ext_ids()
    ):
        meta_getter = AniDB.get_meta_getter(
            identifiable.ext_ids()[AniDB.KEY]
        )

        meta = meta_getter.get()

        db.update_meta([meta])

        info_updated = True

    return info_updated


def media_get_info(db, media_id):
    found, updated = False, False

    identifiable = db.get_media(media_id)
    if identifiable and isinstance(identifiable, Identifiable):
        found = True
        updated = _get_info(db, identifiable)

    return found, updated


def container_get_info(db, container_id):
    found, updated = False, False

    identifiable = db.get_container(container_id)
    if identifiable and isinstance(identifiable, Identifiable):
        found = True
        updated = _get_info(db, identifiable)

    return found, updated


def clear_play_next_list(db):
    WatchingList.remove_all(db)


def get_streams(db, media_id, codec, width, height, start_time):
    streams = None
    media = db.get_media(media_id)

    if media:
        import classes.streaming as streaming

        streams = streaming.get_streams(
            media, codec, width, height, start_time
        )

    return streams
