import http.server
import socketserver
import subprocess
import json
import classes.api as api
from classes.apis.to_dict import DictContainer, DictMedia
from classes.db import DB
import os
import sys

NOT_FOUND_REPLY = {'code': 404, 'message': 'Not found'}
INVALID_REQUEST_REPLY = {'code': 400, 'message': 'Invalid request'}
OK_REPLY = {'code': 200, 'message': 'Ok'}


def epoch_to_httptime(secs):
    from datetime import datetime, timezone

    dt = datetime.fromtimestamp(secs, timezone.utc)

    return dt.strftime('%a, %d %b %Y %H:%M:%S GMT')


def check_if_modified_since(headers, file_path):
    use_cache_304 = False

    if 'If-Modified-Since' in headers.keys():
        from datetime import datetime, timezone

        last_modified = int(os.path.getmtime(file_path))

        b = datetime.fromtimestamp(
            last_modified, timezone.utc
        ).replace(tzinfo=None)
        a = datetime.strptime(
            headers['If-Modified-Since'], '%a, %d %b %Y %H:%M:%S %Z'
        )

        use_cache_304 = b <= a

    return use_cache_304


class Handler(http.server.SimpleHTTPRequestHandler):

    def do_GET(self):
        reply = None
        cache_control = None
        last_modified = None

        db = DB.get_instance()
        db.connect()

        if self.path == "/":
            if check_if_modified_since(self.headers, './example.db'):
                response_code = 304
            else:
                media_library_ids = api.get_media_libraries(db)

                media_libraries = []
                for media_library_id in media_library_ids:
                    media_libraries.append(
                        api.get_container(db, media_library_id)
                    )

                    # temp
                    for media_library in media_libraries:
                        if media_library.title() == "/data/viihde/anime/":
                            break
                    media_libraries.remove(media_library)
                    media_libraries.insert(0, media_library)

                play_next = api.play_next_list(db)

                response_code = 200
                reply = {
                    'play_next_list':  [DictMedia.dict(m) for m in play_next],
                    'media_libraries':
                        [DictContainer.dict(ml) for ml in media_libraries]
                }
                cache_control = "private, must-revalidate, max-age=0"
                last_modified = os.path.getmtime('./example.db')

        elif self.path.startswith("/c/"):
            if check_if_modified_since(self.headers, './example.db'):
                response_code = 304
            else:
                parts = self.path[1:].split("/")
                item_id = parts[-1]

                if item_id and len(parts) == 2:
                    container = api.get_container(db, item_id)

                    if container:
                        response_code = 200
                        reply = DictContainer.dict(container)

                        cache_control = "private, must-revalidate, max-age=0"
                        last_modified = os.path.getmtime('./example.db')
                    else:
                        response_code = 404

                else:
                    response_code = 400

        elif self.path.startswith("/m/"):
            if check_if_modified_since(self.headers, './example.db'):
                response_code = 304
            else:
                parts = self.path[1:].split("/")
                item_id = parts[-1]

                if item_id and len(parts) == 2:
                    media = api.get_media(db, item_id)

                    if media:
                        response_code = 200
                        reply = DictMedia.dict(media)

                        cache_control = "private, must-revalidate, max-age=0"
                        last_modified = os.path.getmtime('./example.db')
                    else:
                        response_code = 404

                else:
                    response_code = 400

        elif self.path.startswith("/playnextlist"):
            if check_if_modified_since(self.headers, './example.db'):
                response_code = 304
            else:
                play_next_list = api.play_next_list(db)

                response_code = 200
                reply = [DictMedia.dict(m) for m in play_next_list]

                cache_control = "private, must-revalidate, max-age=0"
                last_modified = os.path.getmtime('./example.db')

        elif self.path.startswith("/clearplaynextlist"):
            api.clear_play_next_list(db)

            response_code = 200

        elif self.path.startswith("/scan/"):
            parts = self.path[1:].split("/")
            item_id = parts[-1]

            if item_id and len(parts) == 2:
                container_id = api.scan(db, item_id)

                if container_id:
                    response_code = 200
                    reply = DictContainer.dict(
                        api.get_container(db, container_id)
                    )
                else:
                    response_code = 404

            else:
                response_code = 400

        elif self.path.startswith("/identify/"):
            parts = self.path[1:].split("/")
            is_container = parts[1] == "c"
            is_media = parts[1] == "m"
            item_id = parts[-1]

            if item_id and len(parts) == 3 and (is_media or is_container):
                if is_container:
                    found, identified = api.container_identify(db, item_id)
                    if identified:
                        item_dict = DictContainer.dict(
                            api.get_container(db, item_id)
                        )

                if is_media:
                    found, identified = api.media_identify(db, item_id)
                    if identified:
                        item_dict = DictMedia.dict(api.get_media(db, item_id))

                if found:
                    response_code = 200
                    reply = {'identified': identified}
                    if identified:
                        reply = {**reply, **item_dict}
                    else:
                        reply = {**reply, 'data_id': item_id}
                else:
                    response_code = 404

            else:
                response_code = 400

        elif self.path.startswith("/play/"):
            media_ids = self.path.split("/")[-1].split(",")

            if len(media_ids) > 0:
                api.play(db, media_ids)
                response_code = 200
            else:
                response_code = 400

        elif self.path.startswith("/played/"):
            parts = self.path[1:].split("/")
            is_container = parts[1] == "c"
            is_media = parts[1] == "m"
            played = parts[2] == "1"
            item_id = parts[-1]

            if item_id and len(parts) == 4 and (is_media or is_container):
                if is_container:
                    found = api.container_played(db, item_id, played)
                    if found:
                        unplayed_count = 0

                        if not played:
                            unplayed_count = db.get_unplayed_count(item_id)

                        message = {'unplayed_count': unplayed_count}

                if is_media:
                    found = api.media_played(db, item_id, played)

                    if found:
                        message = {'played': played}

                if found:
                    response_code = 200
                    reply = {**message, 'data_id': item_id}
                else:
                    response_code = 404

            else:
                response_code = 400

        elif self.path.startswith("/info/"):
            parts = self.path[1:].split("/")
            is_container = parts[1] == "c"
            is_media = parts[1] == "m"
            item_id = parts[-1]

            if item_id and len(parts) == 3 and (is_media or is_container):
                if is_container:
                    found, updated = api.container_get_info(db, item_id)
                    if updated:
                        item_dict = DictContainer.dict(
                            api.get_container(item_id)
                        )

                if is_media:
                    found, updated = api.media_get_info(item_id)
                    if updated:
                        item_dict = DictMedia.dict(api.get_media(db, item_id))

                if found:
                    response_code = 200
                    reply = item_dict
                else:
                    response_code = 404

            else:
                response_code = 400

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
            response_code = 404
            reply = None
            content_type = None

            file_path = os.path.join(
                sys.path[0],
                os.sep.join(self.path[1:].split("/"))
            )

            if os.path.exists(file_path):
                response_code = 200
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
            response_code = 404

            file_path = os.path.join(
                sys.path[0],
                "html",
                os.sep.join(self.path[1:].split("/"))
            )

            if check_if_modified_since(self.headers, file_path):
                response_code = 304
            else:
                if os.path.exists(file_path):
                    response_code = 200
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

                cache_control = "private, must-revalidate, max-age=0"
                last_modified = os.path.getmtime(file_path)

        else:
            print('ignore', f'"{self.path}"')
            response_code = 400

        db.close()

        if response_code in (200, 304) and reply is None:
            reply = OK_REPLY
        if response_code == 400:
            reply = INVALID_REQUEST_REPLY
        elif response_code == 404:
            reply = NOT_FOUND_REPLY

        if isinstance(reply, dict):
            reply = json.dumps(reply)
            content_type = "text/json"

        if isinstance(reply, str):
            reply = bytes(reply, "utf-8")

        self.protocol_version = 'HTTP/1.1'

        self.send_response(response_code)

        self.send_header("Content-type", content_type)
        if cache_control is not None:
            self.send_header("Cache-Control", cache_control)
        if last_modified is not None:
            self.send_header("Last-Modified", epoch_to_httptime(last_modified))

        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

        # print(self.headers)

        try:
            self.wfile.write(reply)
        except Exception as e:
            print('handler.wfile.write(reply) FAIL!!!!', e)


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
        # 'chromium',
        # f'./html/index.html?api_url=http://{hostName}:{serverPort}'
        f'http://{hostName}:{serverPort}/index.html'
    ])
    httpd.serve_forever()
except KeyboardInterrupt:
    pass

httpd.server_close()
print("Server stopped.")
