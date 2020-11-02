import http.server
import socketserver
import subprocess
import json
import classes.api as api
from classes.apis.to_dict import DictContainer, DictMedia

NOT_FOUND_REPLY = {'code': 404, 'message': 'Not found'}
INVALID_REQUEST_REPLY = {'code': 400, 'message': 'Invalid request'}
OK_REPLY = {'code': 200, 'message': 'Ok'}


class Handler(http.server.SimpleHTTPRequestHandler):

    def send_headers(self, content_type, cache_control):
        self.send_header("Content-type", content_type)
        if cache_control is not None:
            self.send_header("Cache-Control", cache_control)

        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

    def send_body(self, reply):

        if reply:
            if isinstance(reply, str):
                reply = bytes(reply, "utf-8")
            try:
                self.wfile.write(reply)
            except Exception as e:
                print('handler.wfile.write(reply) FAIL!!!!', e)

    def do_GET(self):
        cache_control = None

        if self.path == "/":
            media_libraries = api.get_media_libraries()
            play_next = api.play_next_list()

            code = 200
            reply = json.dumps({
                'play_next_list':  [DictMedia.dict(m) for m in play_next],
                'media_libraries':
                    [DictContainer.dict(ml) for ml in media_libraries]
            })

            content_type = "text/json"

        elif self.path.startswith("/c/"):
            parts = self.path[1:].split("/")
            item_id = parts[-1]

            if item_id and len(parts) == 2:
                container = api.get_container(item_id)

                if container:
                    code = 200
                    reply = json.dumps(DictContainer.dict(container))
                else:
                    code = 404
                    reply = json.dumps(NOT_FOUND_REPLY)

            else:
                code = 400
                reply = json.dumps(INVALID_REQUEST_REPLY)

            content_type = "text/json"

        elif self.path.startswith("/m/"):
            parts = self.path[1:].split("/")
            item_id = parts[-1]

            if item_id and len(parts) == 2:
                media = api.get_media(item_id)

                if media:
                    code = 200
                    reply = json.dumps(DictMedia.dict(media))
                else:
                    code = 404
                    reply = json.dumps(NOT_FOUND_REPLY)

            else:
                code = 400
                reply = json.dumps(INVALID_REQUEST_REPLY)

            content_type = "text/json"

        elif self.path.startswith("/playnextlist"):
            play_next_list = api.play_next_list()

            code = 200
            reply = json.dumps([DictMedia.dict(m) for m in play_next_list])
            content_type = "text/json"

        elif self.path.startswith("/clearplaynextlist"):
            api.clear_play_next_list()

            code = 200
            reply = json.dumps(OK_REPLY)
            content_type = "text/json"

        elif self.path.startswith("/scan/"):
            parts = self.path[1:].split("/")
            item_id = parts[-1]

            if item_id and len(parts) == 2:
                container_id = api.scan(item_id)

                if container_id:
                    code = 200
                    reply = json.dumps(
                        DictContainer.dict(api.get_container(container_id))
                    )
                else:
                    code = 404
                    reply = json.dumps(NOT_FOUND_REPLY)

            else:
                code = 400
                reply = json.dumps(INVALID_REQUEST_REPLY)

            content_type = "text/json"

        elif self.path.startswith("/identify/"):
            parts = self.path[1:].split("/")
            is_container = parts[1] == "c"
            is_media = parts[1] == "m"
            item_id = parts[-1]

            if item_id and len(parts) == 3 and (is_media or is_container):
                if is_container:
                    found, identified = api.container_identify(item_id)
                    if identified:
                        item_dict = DictContainer.dict(api.get_container(item_id))

                if is_media:
                    found, identified = api.media_identify(item_id)
                    if identified:
                        item_dict = DictMedia.dict(api.get_media(item_id))

                if found:
                    code = 200
                    reply = {'identified': identified}
                    if identified:
                        reply = {**reply, **item_dict}
                    reply = json.dumps(reply)
                else:
                    code = 404
                    reply = json.dumps(NOT_FOUND_REPLY)

                content_type = "text/json"

            else:
                code = 400
                reply = json.dumps(INVALID_REQUEST_REPLY)

        elif self.path.startswith("/play/"):
            media_ids = self.path.split("/")[-1].split(",")

            if len(media_ids) > 0:
                api.play(media_ids)
                code = 200
                reply = json.dumps(OK_REPLY)
                content_type = "text/json"
            else:
                code = 400
                reply = json.dumps(INVALID_REQUEST_REPLY)

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
                with open(file_path, "rb") as f:
                    reply = f.read()

                content_type = f"image/{file_path[-3:]}"
                cache_control = "private, max-age=604800"
        elif self.path in (
            "/images/play-icon.png",
            "/scripts/page_builder.js",
            "/scripts/scripts.js",
            "/styles/styles.css",
            "/index.html"
        ):
            import os
            import sys
            code = 404

            file_path = os.path.join(
                sys.path[0],
                "html",
                os.sep.join(self.path[1:].split("/"))
            )

            if os.path.exists(file_path):
                code = 200
                with open(file_path, "rb") as f:
                    reply = f.read()

            if self.path.endswith(".png"):
                content_type = "image/png"
            elif self.path.endswith(".js"):
                content_type = "text/javascript"
            elif self.path.endswith(".css"):
                content_type = "text/css"
            elif self.path.endswith(".html"):
                content_type = "text/html"

        else:
            print('ignore', f'"{self.path}"')
            code = 400
            reply = None
            content_type = None

        # if isinstance(reply, dict):
        #    reply = json.dumps(reply)
        #    content_type = "text/json"

        if code:
            self.send_response(code)

        if content_type or cache_control:
            self.send_headers(content_type, cache_control)

        if reply:
            self.send_body(reply)


# https://stackoverflow.com/questions/166506/finding-local-ip-addresses-using-pythons-stdlib
def get_ip():
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP


hostName = get_ip()

try:
    serverPort = 8086
    httpd = socketserver.TCPServer((hostName, serverPort), Handler)
    print('skip', serverPort)
except OSError:
    for port in range(8087, 8097):
        serverPort = port
        try:
            httpd = socketserver.TCPServer((hostName, serverPort), Handler)
            break
        except OSError:
            print('skip', serverPort)

print(f"Server started http://{hostName}:{serverPort}")

try:
    subprocess.Popen([
        'firefox',
        # f'./html/index.html?api_url=http://{hostName}:{serverPort}'
        f'http://{hostName}:{serverPort}/index.html'
    ])
    httpd.serve_forever()
except KeyboardInterrupt:
    pass

httpd.server_close()
print("Server stopped.")
