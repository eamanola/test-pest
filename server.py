import http.server
import socketserver
from urllib.parse import urlparse, parse_qs
import time
from classes.ui.media_ui import MediaUI
from classes.ui.container_ui import ContainerUI
from classes.scanner import Scanner
from classes.container import MediaLibrary, Show, Season, Extra
from classes.media import Movie, Episode
from classes.identifiable import Identifiable
from classes.db import DB
import os
import sys
from classes.identifier import Identifier
from classes.ext_apis.anidb import AniDB
import subprocess
from classes.watchinglist import WatchingList


def collect_objs(con, containers=[], media=[]):
    containers = containers + con.containers
    media = media + con.media

    for container in con.containers:
        containers, media = collect_objs(container, containers, media)

    return containers, media


class Handler(http.server.SimpleHTTPRequestHandler):

    def html(self, params):
        if self.path == "/":
            params = {
                'c': ["d16c4b170f395bcdeaedcd5c9786eb01"]
            }

        if 'c' in params:
            container_id = params['c'][0]

            db = DB.get_instance()
            db.connect()
            container = db.get_container(container_id)

            if isinstance(container, (Extra, Season)):
                parent = container.parent()
                while parent and not isinstance(parent, Identifiable):
                    parent.set_parent(db.get_container(parent.parent()))
                    parent = parent.parent()

            db.close()

            page = ContainerUI.html_page(container)

            if container.__class__.__name__ != "MediaLibrary":
                media_library = MediaLibrary(container.path())
            else:
                media_library = None

        elif 'm' in params:
            media_id = params['m'][0]
            media = None
            show = None
            parents = []
            episode_meta = None

            db = DB.get_instance()
            db.connect()
            media = db.get_media(media_id)

            if isinstance(media, Episode):
                media.set_parent(db.get_container(media.parent()))
                parent = media.parent()
                while parent and not isinstance(parent, Identifiable):
                    parent.set_parent(db.get_container(parent.parent()))
                    parent = parent.parent()

            db.close()

            page = MediaUI.html_page(media)
            if media.parent() and media.parent().path():
                media_library = MediaLibrary(media.parent().path())
            else:
                media_library = None

        play_next_list_str = ""
        if self.path == "/":
            db = DB.get_instance()
            db.connect()

            play_next = WatchingList.get_play_next_list(db)

            for media in play_next:
                if isinstance(media, Episode):
                    parent = media.parent()
                    while parent and not isinstance(parent, Identifiable):
                        parent.set_parent(db.get_container(parent.parent()))
                        parent = parent.parent()

                play_next_list_str = (''.join([
                    play_next_list_str,
                    MediaUI.html_line(media)
                ]))

            cur = db.conn.cursor()

            sql = 'select id from containers where type="MediaLibrary"'
            cur.execute(sql)

            page = ""

            medialibs = cur.fetchall()
            medialibs.reverse()

            for media_lib in medialibs:
                page = f"""
                {page}
                {ContainerUI.html_page(db.get_container(media_lib[0]))}
                """

            db.close()

        if media_library:
            media_library = f'''
                <a href="/?c={media_library.id()}" >
                    {media_library.title()}
                </a>'''
        else:
            media_library = ""

        return f"""
            <!DOCTYPE html>
            <html>
                <head>
                    <title>test-pest</title>
                    <link rel="stylesheet" href="styles.css">
                </head>
                <body>
                    <a href="/">Home</a>
                    {media_library}
                    <div id="add-to-play-list"></div>
                    <button id="play-button">Play</button>
                    <button id="clear-add-to-play-list-button">Clear</button>
                    <div id="play-next-list">{play_next_list_str}</div>
                    {page}
                    <script type="text/javascript" src="./scripts.js"></script>
                </body>
            </html>
        """

    def do_GET(self):
        params = parse_qs(urlparse(self.path).query)
        page = "Unknown"
        id = None

        if (
            'c' in params or
            'm' in params or
            self.path == "/"
        ):
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()

            self.wfile.write(bytes(self.html(params), "utf-8"))

        elif 's' in params:
            self.send_response(200)
            self.send_header("Content-type", "text/json")
            self.end_headers()

            container_id = params['s'][0]

            db = DB.get_instance()
            db.connect()

            container = db.get_container(container_id)
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

                db.update_containers(containers, update_identifiables=False)
                db.update_media(
                    media,
                    update_identifiables=False,
                    update_media_states=False
                )

            db.close()

            self.wfile.write(
                bytes(
                    f'''{{
                        "action":"scan",
                        "data_id":"{container_id}",
                        "message":"{container.title()} updated"
                    }}'''.replace("\n", " "),
                    "utf-8"
                )
            )
        elif 'i' in params:
            self.send_response(200)
            self.send_header("Content-type", "text/json")
            self.end_headers()

            identifiable_id = params['i'][0]

            error = 0
            message = ""

            db = DB.get_instance()
            db.connect()

            container = db.get_container(identifiable_id)
            if not container:
                media = db.get_media(identifiable_id)

            item = container if container else media

            if not item:
                error = 1
                message = "Not Found"

            if not error:
                media_type = AniDB.TV_SHOW if container else AniDB.MOVIE
                if isinstance(item, Movie):
                    show_name = item.title()
                elif isinstance(item, Show):
                    show_name = container.show_name()
                print(media_type)
                anidb_id = Identifier(AniDB).guess_id(
                    db,
                    show_name,
                    item.year(),
                    media_type
                )

                if anidb_id:
                    item.ext_ids()[AniDB.KEY] = anidb_id

                if container:
                    db.update_containers([container])
                else:
                    db.update_media([media])

                message = f"anidb is {anidb_id}"

            db.close()
            self.wfile.write(
                bytes(
                    f'''{{
                        "action":"identify",
                        "data_id":"{identifiable_id}",
                        "error":"{error}",
                        "message": "{message}"
                    }}'''.replace("\n", " "),
                    "utf-8"
                )
            )
        elif 'p' in params:
            self.send_response(200)
            self.send_header("Content-type", "text/json")
            self.end_headers()

            to_play = params['p'][0].split(",")
            media = []

            error = 0
            message = ""

            db = DB.get_instance()
            db.connect()

            for item in to_play:
                m = db.get_media(item)
                if m:
                    media.append(m)

            if len(media) == 0:
                error = 1
                message = "Nothing to play"
            else:
                message = f"playing {', '.join([m.title() for m in media])}"

                file_paths = [
                    f'{os.path.join(m.parent().path(), m.file_path())}'
                    for m in media
                ]

                cmd_vlc = [
                    'vlc',
                    '--fullscreen',
                    '--mouse-hide-timeout 3000',
                    '-q'
                ] + file_paths

                cmd_mpv = [
                    'mpv',
                    '--fullscreen',
                    '--slang=en,eng'
                ] + file_paths

                cmd_play = [
                    os.path.join(sys.path[0], 'play.sh')
                ] + file_paths

                cmd = cmd_play
                subprocess.Popen(cmd)
                print(" ".join(cmd))

                # os.system(cmd)
                WatchingList.started_play(db, media)
            db.close()

            self.wfile.write(
                bytes(
                    f'''{{
                        "action":"play",
                        "data_id":"{params['p']}",
                        "error":"{error}",
                        "message": "{message}"
                    }}'''.replace("\n", " "),
                    "utf-8"
                )
            )

        elif 'pa' in params or 'pr' in params:
            self.send_response(200)
            self.send_header("Content-type", "text/json")
            self.end_headers()

            add = 'pa' in params
            remove = 'pr' in params
            media_id = params['pa'][0] if add else params['pr'][0]

            db = DB.get_instance()
            db.connect()

            media = db.get_media(media_id)
            media.set_played(add)
            db.update_media([media])

            db.close()

            message = f"""
                {media.title()} marked {"played" if add else "unplayed"}
            """

            self.wfile.write(
                bytes(
                    f'''{{
                        "action":"played",
                        "data_id":"{media_id}",
                        "message": "{message}"
                    }}'''.replace("\n", " "),
                    "utf-8"
                )
            )

        elif 'gic' in params or 'gim' in params:

            self.send_response(200)
            self.send_header("Content-type", "text/json")
            self.end_headers()

            db = DB.get_instance()
            db.connect()

            if 'gic' in params:
                message = f"get container {params['gic'][0]}"
                identifiable = db.get_container(params['gic'][0])

            elif 'gim' in params:
                message = f"get media {params['gim'][0]}"
                identifiable = db.get_media(params['gim'][0])

            if (
                identifiable and
                isinstance(identifiable, Identifiable) and
                AniDB.KEY in identifiable.ext_ids()
            ):
                meta_getter = AniDB.get_meta_getter(
                    identifiable.ext_ids()[AniDB.KEY]
                )
                meta = meta_getter.get()
                db.save_meta([meta])
                message = "completed"
            else:
                message = "fail"

            db.close()
            self.wfile.write(
                bytes(
                    f'''{{
                        "action":"get_info",
                        "data_id":"{params['gic'][0]
                            if 'gic' in params else params['gim'][0]}",
                        "message": "{message}"
                    }}'''.replace("\n", " "),
                    "utf-8"
                )
            )
        elif self.path == "/scripts.js":

            self.send_response(200)
            self.send_header("Content-type", "text/javascript")
            self.end_headers()

            f = open(os.path.join(sys.path[0], 'scripts.js'), "rb")
            self.wfile.write(f.read())
            f.close()
        elif self.path == "/styles.css":

            self.send_response(200)
            self.send_header("Content-type", "text/css")
            self.end_headers()

            f = open(os.path.join(sys.path[0], 'styles.css'), "rb")
            self.wfile.write(f.read())
            f.close()

        elif (
            (
                self.path.startswith("/images/thumbnails/") and
                self.path.endswith(".png")
            ) or (
                self.path.startswith("/images/posters/") and
                self.path.endswith(".jpg")
            )
        ):
            file_path = os.path.join(
                sys.path[0],
                os.sep.join(self.path[1:].split("/"))
            )

            if os.path.exists(file_path):
                self.send_response(200)
                self.send_header("Content-type", f"image/{file_path[-3:]}")
                self.end_headers()

                f = open(file_path, "rb")
                self.wfile.write(f.read())
                f.close()
            else:
                self.send_response(404)
                self.end_headers()

        elif self.path == "/favicon.ico":
            pass
        else:
            print('ignore', self.path)


hostName = "localhost"

try:
    serverPort = 8080
    httpd = socketserver.TCPServer((hostName, serverPort), Handler)
except OSError:
    serverPort = 8083
    httpd = socketserver.TCPServer((hostName, serverPort), Handler)

print("Server started http://%s:%s" % (hostName, serverPort))

try:
    subprocess.Popen(['firefox', f'http://{hostName}:{serverPort}'])
    httpd.serve_forever()
except KeyboardInterrupt:
    pass

httpd.server_close()
print("Server stopped.")
