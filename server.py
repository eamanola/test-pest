import http.server
import socketserver
from urllib.parse import urlparse, parse_qs
import time
from classes.ui.media_ui import MediaUI
from classes.ui.container_ui import ContainerUI
from classes.scanner import Scanner
from classes.container import MediaLibrary, Show, Season, Extra
from classes.db import DB
import os
import sys


def collect_objs(con, containers=[], media=[]):
    containers = containers + con.containers
    media = media + con.media

    for container in con.containers:
        containers, media = collect_objs(container, containers, media)

    return containers, media


class Handler(http.server.SimpleHTTPRequestHandler):

    def html(self, params):
        if 'c' in params:
            container_id = params['c'][0]

            db = DB.get_instance()
            db.connect()
            container = db.get_container(container_id)
            db.close()

            page = ContainerUI.html_page(container) if container else "errorrs"
        elif 'm' in params:
            media_id = params['m'][0]

            db = DB.get_instance()
            db.connect()
            media = db.get_media(media_id)
            db.close()

            page = f'''
                {media.file_path()} <br/>
                {media.title()} <br/>
                {media.thumbnail()} <br/>
                {media.parent().title() if media.parent() else ""} <br/>
            '''

        return f"""
            <!DOCTYPE html>
            <html>
                <head>
                    <title>test-pest</title>
                    <link rel="stylesheet" href="styles.css">
                </head>
                <body>
                    <p>Request: {self.path}</p>
                    <p>Params: {params}</p>
                    {page}
                    <script type="text/javascript" src="./scripts.js"></script>
                </body>
            </html>
        """

    def do_GET(self):
        if self.path == "/":
            self.path = "/?c=d16c4b170f395bcdeaedcd5c9786eb01"

        params = parse_qs(urlparse(self.path).query)
        page = "Unknown"
        id = None

        if (
            'c' in params or
            'm' in params
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
                containers.append(container)

                db.create_containers_table()
                db.create_media_table()

                db.update_containers(containers)
                db.update_media(media)

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
            self.path.startswith("/images/thumbnails/") and
            self.path.endswith(".png")
        ):
            self.send_response(200)
            self.send_header("Content-type", "image/png")
            self.end_headers()

            f = open(os.path.join(
                sys.path[0],
                os.sep.join(self.path[1:].split("/"))
            ), "rb")
            self.wfile.write(f.read())
            f.close()

        elif self.path.endswith(".jpg"):
            print('ignore image')
        else:
            print('ignore', self.path)


hostName = "localhost"

try:
    serverPort = 8080
    httpd = socketserver.TCPServer((hostName, 8080), Handler)
except OSError:
    serverPort = 8083
    httpd = socketserver.TCPServer((hostName, 8083), Handler)

print("Server started http://%s:%s" % (hostName, serverPort))

try:
    httpd.serve_forever()
except KeyboardInterrupt:
    pass

httpd.server_close()
print("Server stopped.")
