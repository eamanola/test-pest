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
from datetime import datetime
import classes.api as api

# deprecated


class Handler(http.server.SimpleHTTPRequestHandler):

    def html(self, params):
        if self.path == "/":
            params = {
                'c': ["d16c4b170f395bcdeaedcd5c9786eb01"]
            }

        if 'c' in params:
            container_id = params['c'][0]

            code, container = api.get_container(container_id)

            page = ContainerUI.html_page(container)

            if container.__class__.__name__ != "MediaLibrary":
                media_library = MediaLibrary(container.path())
            else:
                media_library = None

        elif 'm' in params:
            media_id = params['m'][0]

            code, media = api.get_media(media_id)

            page = MediaUI.html_page(media)

            if media.parent() and media.parent().path():
                media_library = MediaLibrary(media.parent().path())
            else:
                media_library = None

        play_next_list_str = ""
        if self.path == "/":
            code, play_next = api.play_next_list()

            for media in play_next:

                play_next_list_str = (''.join([
                    play_next_list_str,
                    MediaUI.html_line(media)
                ]))

            if play_next_list_str:
                play_next_list_str = (''.join([
                    '<div class="container page header">',
                    'Day\'s Menu ', datetime.now().strftime("%H:%M"),
                    '</div>\n',
                    play_next_list_str,
                    '<div><button id="clear-play-next-list-button">',
                    'Clear</button></div>'
                ]))

            db = DB.get_instance()
            db.connect()

            cur = db.conn.cursor()

            sql = 'select id from containers where type="MediaLibrary"'
            cur.execute(sql)

            page = ""

            medialibs = cur.fetchall()

            for media_lib in medialibs:
                ml = db.get_container(media_lib[0])

                for c in ml.containers:
                    c.set_unplayed_count(db.get_unplayed_count(c.id()))

                new_page = [page, ContainerUI.html_page(ml)]
                if ml.path() == "/data/viihde/anime/":
                    new_page.reverse()

                page = ''.join(new_page)

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
                    <link rel="stylesheet" href="/html/styles/styles.css">
                </head>
                <body class="grid">
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

            api.scan(container_id)

            self.wfile.write(
                bytes(
                    f'''{{
                        "action":"scan",
                        "data_id":"{container_id}"
                    }}'''.replace("\n", " "),
                    "utf-8"
                )
            )
        elif 'i' in params:
            self.send_response(200)
            self.send_header("Content-type", "text/json")
            self.end_headers()

            identifiable_id = params['i'][0]

            db = DB.get_instance()
            db.connect()

            if db.get_container(identifiable_id) is not None:
                code, reply = api.container_identify(identifiable_id)
            else:
                code, reply = api.media_identify(identifiable_id)

            self.wfile.write(
                bytes(
                    f'''{{
                        "action":"identify",
                        "data_id":"{identifiable_id}",
                        "message":"{reply}"
                    }}'''.replace("\n", " "),
                    "utf-8"
                )
            )
        elif 'p' in params:
            to_play = params['p'][0].split(",")

            code, reply = api.play(to_play)

            self.send_response(code)
            self.send_header("Content-type", "text/json")
            self.end_headers()

            self.wfile.write(
                bytes(
                    f'''{{
                        "action":"play",
                        "message": "{reply}"
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
            item_id = params['pa'][0] if add else params['pr'][0]

            if params['type'][0] == "media":
                code, reply = api.media_played(item_id, add is True)
            elif params['type'][0] == "container":
                code, reply = api.container_played(item_id, add is True)

            message = f"""
                marked {"played" if add else "unplayed"}
            """

            self.wfile.write(
                bytes(
                    f'''{{
                        "action":"played",
                        "data_id":"{item_id}",
                        "message": "{message}"
                    }}'''.replace("\n", " "),
                    "utf-8"
                )
            )

        elif 'gic' in params or 'gim' in params:

            self.send_response(200)
            self.send_header("Content-type", "text/json")
            self.end_headers()

            if 'gic' in params:
                code, reply = api.container_get_info(params['gic'][0])

            elif 'gim' in params:
                code, reply = api.media_get_info(params['gim'][0])

            self.wfile.write(
                bytes(
                    f'''{{
                        "action":"get_info",
                        "data_id":"{params['gic'][0]
                            if 'gic' in params else params['gim'][0]}",
                        "message": "{reply}"
                    }}'''.replace("\n", " "),
                    "utf-8"
                )
            )
        elif self.path == "/cpn":
            import re
            self.send_response(200)
            self.send_header("Content-type", "text/json")
            self.end_headers()

            api.clear_play_next_list()

            ret = f'''{{
                "action":"clear watchlist",
                "message": "cleared"
            }}'''

            self.wfile.write(
                bytes(
                    re.sub(r"\s+", " ", ret),
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
        elif self.path == "/html/styles/styles.css":

            self.send_response(200)
            self.send_header("Content-type", "text/css")
            self.end_headers()

            f = open(os.path.join(
                sys.path[0],
                'html',
                'styles',
                'styles.css'
            ), "rb")
            self.wfile.write(f.read())
            f.close()

        elif (
            (
                self.path.startswith("/images/thumbnails/") and
                self.path.endswith(".png")
            )
            or (
                self.path.startswith("/images/posters/") and
                self.path.endswith(".jpg")
            )
            or self.path == "/html/images/play-icon.png"
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
            self.send_response(400)
            self.end_headers()
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
