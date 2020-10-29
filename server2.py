import http.server
import socketserver
import subprocess
import json
import classes.api as api
from classes.apis.to_dict import DictContainer, DictMedia


def send_headers(handler, code, content_type):
    handler.send_response(code)
    handler.send_header("Content-type", content_type)
    handler.send_header("Access-Control-Allow-Origin", "*")
    handler.end_headers()


def send_body(handler, message):
    import re

    handler.wfile.write(bytes(
        re.sub(r'\s+', " ", message),
        "utf-8"
    ))


class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            code, media_libraries = api.get_media_libraries()
            code, play_next = api.play_next_list()

            reply = json.dumps({
                'play_next_list':  [DictMedia.dict(m) for m in play_next],
                'media_libraries':
                    [DictContainer.dict(ml) for ml in media_libraries]
            })

            content_type = "text/json"

        elif self.path.startswith("/c/"):
            item_id = self.path.split("/")[-1]

            code, container = api.get_container(item_id)
            reply = None
            content_type = "text/json"

            if container:
                reply = json.dumps(DictContainer.dict(container))

        elif self.path.startswith("/m/"):
            item_id = self.path.split("/")[-1]

            code, media = api.get_media(item_id)
            reply = None
            content_type = "text/json"

            if media:
                reply = json.dumps(DictMedia.dict(media))

        elif self.path.startswith("/playnextlist"):
            code, play_next_list = api.play_next_list()
            reply = json.dumps([DictMedia.dict(m) for m in play_next_list])
            content_type = "text/json"

        elif self.path.startswith("/clearplaynextlist"):
            code, reply = api.clear_play_next_list()
            content_type = "text/json"

        elif self.path.startswith("/scan/"):
            container_id = self.path.split("/")[-1]

            code, container = api.scan(container_id)
            reply = None
            content_type = "text/json"

            if container:
                reply = json.dumps(DictContainer.dict(container))

        elif self.path.startswith("/identify/"):
            parts = self.path[1:].split("/")
            is_container = parts[1] == "c"
            is_media = parts[1] == "m"
            item_id = parts[-1]

            code = 400
            reply = {'data_id': item_id, 'identified': False}
            content_type = "text/json"

            if is_container:
                code, update_item = api.container_identify(item_id)
                if update_item:
                    reply = {
                        'identified': True,
                        **DictContainer.dict(update_item)
                    }

            elif is_media:
                code, update_item = api.media_identify(item_id)
                if update_item:
                    reply = {
                        'identified': True,
                        **DictMedia.dict(update_item)
                    }

            reply = json.dumps(reply)

        elif self.path.startswith("/play/"):
            media_ids = self.path.split("/")[-1].split(",")

            code, reply = api.play(media_ids)
            content_type = "text/json"

        elif self.path.startswith("/played/"):
            parts = self.path[1:].split("/")
            is_container = parts[1] == "c"
            is_media = parts[1] == "m"
            played = parts[2] == "1"
            item_id = parts[-1]

            code = 400
            reply = None
            content_type = "text/json"

            if is_container:
                code, unplayed_count = api.container_played(item_id, played)
                reply = {'unplayed_count': unplayed_count}

            elif is_media:
                code, played = api.media_played(item_id, played)
                reply = {'played': played}

            if reply:
                reply = json.dumps({**reply, 'data_id': item_id})

        elif self.path.startswith("/info/"):
            parts = self.path[1:].split("/")
            is_container = parts[1] == "c"
            is_media = parts[1] == "m"
            item_id = parts[-1]

            code = 400
            reply = None
            content_type = "text/json"

            if is_container:
                code, update_item = api.container_get_info(item_id)
                if update_item:
                    reply = json.dumps(DictContainer.dict(update_item))

            elif is_media:
                code, update_item = api.media_get_info(item_id)
                if update_item:
                    reply = json.dumps(DictMedia.dict(update_item))

        elif (
            (
                self.path.startswith("/images/thumbnails/")
                and self.path.endswith(".png")
            )
            or (
                self.path.startswith("/images/posters/")
                and self.path.endswith(".jpg")
            )
            or self.path == "/html/images/play-icon.png"
        ):
            import os
            import sys
            code = 404
            reply = None
            content_type = None

            file_path = os.path.join(
                sys.path[0],
                os.sep.join(self.path[1:].split("/"))
            )

            if os.path.exists(file_path):
                code = 200
                reply = None
                content_type = f"image/{file_path[-3:]}"

                f = open(file_path, "rb")
                self.wfile.write(f.read())
                f.close()

        else:
            print('ignore', f'"{self.path}"')
            code = 400
            reply = None
            content_type = None

        if code:
            send_headers(self, code, content_type)

        if reply:
            send_body(self, reply)


hostName = "localhost"

try:
    serverPort = 8086
    httpd = socketserver.TCPServer((hostName, serverPort), Handler)
except OSError:
    serverPort = 8089
    httpd = socketserver.TCPServer((hostName, serverPort), Handler)

print(f"Server started http://{hostName}:{serverPort}")

try:
    subprocess.Popen([
        'firefox',
        f'./html/index.html?port={serverPort}'
    ])
    httpd.serve_forever()
except KeyboardInterrupt:
    pass

httpd.server_close()
print("Server stopped.")
