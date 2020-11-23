from models.containers import Extra, Season, Show, MediaLibrary
from models.media import Media, Movie, Episode
from models.identifiable import Identifiable
from classes.watchinglist import WatchingList
from metafinder.anidb import AniDB


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
    import sqlite3

    cur = db.conn.cursor()
    sql = 'select id from containers where type="MediaLibrary"'

    try:
        cur.execute(sql)
    except sqlite3.OperationalError:
        print('gen base tables')
        db.create_media_table()
        db.create_containers_table()
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


def scan(
    db,
    container_id,
    update_identifiables=False,
    overwrite_media_states=False
):
    from mediafinder.scanner import Scanner

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
                update_identifiables=update_identifiables
            )
            db.update_media(
                media,
                update_identifiables=update_identifiables,
                overwrite_media_states=overwrite_media_states
            )

            scanned = result.id()

    return scanned


def _identify(db, identifiable, media_type):
    from metafinder.identifier import Identifier

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
            'vlc', '--fullscreen'  # , '--mouse-hide-timeout 3000'
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
        meta = AniDB.get_meta_getter().get(identifiable.ext_ids()[AniDB.KEY])

        if meta:
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


def get_streams(db, media_id, codec, width, height, start_time=0):
    streams = None
    media = db.get_media(media_id)

    if media:
        import classes.streaming as streaming

        streams = streaming.get_streams(
            media, codec, width, height, start_time
        )

        if streams:
            WatchingList.started_play(db, [media])

    return streams


def get_video_stream(
    db,
    media_id,
    codec,
    width,
    height,
    transcode,
    start_time=0,
    subtitle_index=None
):
    stream = None
    media = db.get_media(media_id)

    if media:
        if transcode:
            import classes.streaming as streaming

            stream = streaming.get_video_stream(
                media, codec, width, height, start_time, subtitle_index
            )
        else:
            import os
            file_path = os.path.join(media.parent().path(), media.file_path())
            stream = file_path if os.path.exists(file_path) else None

    return stream


def get_audio_stream(db, media_id, stream_index, start_time=0):
    stream = None
    media = db.get_media(media_id)

    if media:
        import classes.streaming as streaming

        stream = streaming.get_audio_stream(media, stream_index, start_time)

    return stream


def get_subtitle(db, media_id, type, stream_index):
    subtitle = None
    media = db.get_media(media_id)

    if media:
        import classes.streaming as streaming

        subtitle = streaming.get_subtitle(media, type, stream_index)

    return subtitle


def get_font(db, media_id, font_name):
    font = None
    media = db.get_media(media_id)

    if media:
        import classes.streaming as streaming

        font = streaming.get_font(media, font_name)

    return font


def add_media_library(db, media_library_path):
    import os
    import sqlite3

    success = False

    if os.path.exists(media_library_path):
        if os.path.isfile(media_library_path):
            path = os.path.dirname(media_library_path)
        else:
            path = media_library_path

        if not path.endswith(os.path.sep):
            path = path + os.path.sep

        media_library = MediaLibrary(path)

        try:
            existing = db.get_container(media_library.id())
        except sqlite3.OperationalError:
            print('gen base tables')
            db.create_media_table()
            db.create_containers_table()

        if existing is None:
            db.update_containers([media_library])

        scanned = scan(db, media_library.id(), update_identifiables=True)
        if scanned is not None:
            media_library = db.get_container(media_library.id())

            try:
                test_movie = Movie("/foo", "bar", False)
                _identify(db, test_movie, None)
                print('exists')
            except sqlite3.OperationalError:
                import metafinder.generate_ext_title_to_id_dbs
                metafinder.generate_ext_title_to_id_dbs.generate_table(
                    db, AniDB
                )
                print('generated')

            updated_containers = []
            for c in media_library.containers:
                if isinstance(c, Identifiable):
                    con = db.get_container(c.id())
                    anidb_id = _identify(db, con, AniDB.TV_SHOW)
                    if anidb_id:
                        con.ext_ids()[AniDB.KEY] = anidb_id
                        _get_info(db, con)
                        updated_containers.append(con)

            if len(updated_containers):
                db.update_containers(updated_containers)

            updated_media = []
            for m in media_library.media:
                if isinstance(m, Identifiable):
                    anidb_id = _identify(db, m, AniDB.MOVIE)
                    if anidb_id:
                        m.ext_ids()[AniDB.KEY] = anidb_id
                        _get_info(db, m)
                        updated_media.append(m)

            if len(updated_media):
                db.update_media(updated_media)

        success = True

    return success
