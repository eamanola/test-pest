import http.server
import socketserver
from urllib.parse import urlparse, parse_qs
import time
from classes.ui.media_ui import MediaUI
from classes.ui.container_ui import ContainerUI
from classes.db import DB
import os
import sys


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
            page = "media"
            id = params['m']

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

        elif (
            self.path == "/scripts.js"
        ):

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
