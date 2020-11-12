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


def mime_type(file_name):
    content_type = None

    if file_name.endswith(".png"):
        content_type = "image/png"
    elif file_name.endswith(".jpg"):
        content_type = "image/jpg"
    elif file_name.endswith(".vtt"):
        content_type = "text/vtt"
    elif file_name.endswith(".webm"):
        content_type = "video/webm"
    elif file_name.endswith(".mkv"):
        content_type = "video/x-matroska"
    elif file_name.endswith(".mp4"):
        content_type = "video/mp4"
    elif file_name.endswith(".opus"):
        content_type = "audio/ogg"
    elif file_name.endswith(".gif"):
        content_type = "image/gif"
    elif file_name.endswith(".js"):
        content_type = "text/javascript"
    elif file_name.endswith(".css"):
        content_type = "text/css"
    elif file_name.endswith(".html"):
        content_type = "text/html"
    elif file_name.endswith(".wasm"):
        content_type = "application/wasm"
    elif file_name.endswith((".otf", ".OTF")):
        content_type = "application/vnd.ms-opentype"
    elif file_name.endswith((".ttf", ".TTF")):
        content_type = "application/x-truetype-font"

    return content_type


class Handler(http.server.SimpleHTTPRequestHandler):

    def revalidate_client_cache(self, file_path=None):
        response_code = None

        if 'If-None-Match' in self.headers.keys():
            if file_path is not None:
                from hashlib import sha256

                with open(file_path, "rb") as f:
                    _bytes = f.read()

                etag = sha256(_bytes).hexdigest()
            else:
                etag = DB.get_instance().version()

            if f'"{etag}"' == self.headers['If-None-Match']:
                response_code = 304

        elif 'If-Modified-Since' in self.headers.keys():
            from datetime import datetime, timezone

            if file_path is not None:
                last_modified = int(os.path.getmtime(file_path))
            else:
                last_modified = DB.get_instance().last_modified()

            dt_last_modified = datetime.fromtimestamp(
                last_modified, timezone.utc
            ).replace(tzinfo=None)
            dt_if_modified_since = datetime.strptime(
                self.headers['If-Modified-Since'], '%a, %d %b %Y %H:%M:%S %Z'
            )

            if dt_last_modified <= dt_if_modified_since:
                response_code = 304
        # elif 'If-Unmodified-Since', 'If-Match'

        # print('revalidate_client_cache:', response_code)
        return response_code

    def do_GET(self):
        reply = None
        send_file_path = None
        cache_control = None
        last_modified = None
        etag = None

        db = DB.get_instance()
        db.connect()

        if self.path in ("/", ""):
            self.path = "/index.html"

        if self.path == "/frontpage":
            response_code = self.revalidate_client_cache()

            if response_code is None:
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
                # last_modified = db.last_modified()
                etag = db.version()

        elif self.path.startswith("/c/"):
            response_code = self.revalidate_client_cache()

            if response_code is None:
                parts = self.path[1:].split("/")
                item_id = parts[-1]

                if item_id and len(parts) == 2:
                    container = api.get_container(db, item_id)

                    if container:
                        response_code = 200
                        reply = DictContainer.dict(container)

                        cache_control = "private, must-revalidate, max-age=0"
                        # last_modified = db.last_modified()
                        etag = db.version()
                    else:
                        response_code = 404

                else:
                    response_code = 400

        elif self.path.startswith("/m/"):
            response_code = self.revalidate_client_cache()

            if response_code is None:
                parts = self.path[1:].split("/")
                item_id = parts[-1]

                if item_id and len(parts) == 2:
                    media = api.get_media(db, item_id)

                    if media:
                        response_code = 200
                        reply = DictMedia.dict(media)

                        cache_control = "private, must-revalidate, max-age=0"
                        # last_modified = db.last_modified()
                        etag = db.version()
                    else:
                        response_code = 404

                else:
                    response_code = 400

        elif self.path.startswith("/playnextlist"):
            response_code = self.revalidate_client_cache()

            if response_code is None:
                play_next_list = api.play_next_list(db)

                response_code = 200
                reply = [DictMedia.dict(m) for m in play_next_list]

                cache_control = "private, must-revalidate, max-age=0"
                # last_modified = db.last_modified()
                etag = db.version()

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
                            api.get_container(db, item_id)
                        )

                if is_media:
                    found, updated = api.media_get_info(db, item_id)
                    if updated:
                        item_dict = DictMedia.dict(api.get_media(db, item_id))

                if found:
                    response_code = 200
                    reply = item_dict
                else:
                    response_code = 404

            else:
                response_code = 400

        elif self.path.startswith("/streams/"):
            parts = self.path[1:].split("/")
            codec = parts[1]
            width = int(parts[2])
            height = int(parts[3])
            media_id = parts[4]

            if (media_id and codec and width and height and len(parts) == 5):
                streams = api.get_streams(
                    db,
                    media_id,
                    codec,
                    width,
                    height
                )
                if streams:
                    reply = streams
                    response_code = 200
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
            or self.path.startswith("/video/")
            or self.path.startswith(
                ("/tmp/video_", "/tmp/audio_", "/tmp/subtitle_")
            )
            or (
                self.path.startswith("/audio/")
                and self.path.endswith(".opus")
            )
            or (
                self.path.startswith("/subtitles/")
                and self.path.endswith(".vtt")
            )
            or (
                self.path.startswith("/fonts/")
                and self.path.endswith((".otf", ".OTF", ".ttf", ".TTF"))
            )
        ):
            response_code = 404
            reply = None
            content_type = None

            path = [sys.path[0]]
            if self.path.startswith(
                ("/video/", "/audio/", "/subtitles/", "/tmp/", "/fonts/")
            ):
                path.append("streams")
            path = path + self.path[1:].split("/")

            file_path = os.sep.join(path).replace("%20", " ")

            if os.path.exists(file_path):
                response_code = 200
                send_file_path = file_path

                content_type = mime_type(file_path)

                cache_control = "private, max-age=604800"
                if self.path.startswith("/tmp/"):
                    cache_control = "private, must-revalidate, max-age=0"

        elif (
            self.path in (
                "/images/play-icon.png",
                "/images/loading.gif",
                "/scripts/page_builder.js",
                "/scripts/scripts.js",
                "/styles/styles.css",
                "/index.html"
            )
            or self.path.startswith("/scripts/octopus-ass")
            or self.path == "/out.ass"
        ):
            response_code = 404

            file_path = os.path.join(
                sys.path[0],
                "html",
                os.sep.join(self.path[1:].split("/"))
            )

            response_code = self.revalidate_client_cache(file_path=file_path)

            if response_code is None:
                if os.path.exists(file_path):
                    response_code = 200
                    with open(file_path, "rb") as f:
                        reply = f.read()

                content_type = mime_type(file_path)

                if content_type is None:
                    content_type = "application/octet-stream"

                cache_control = "private, must-revalidate, max-age=0"

                if content_type.startswith("image"):
                    cache_control = "private, max-age=604800"

                last_modified = os.path.getmtime(file_path)

                send_file_path = file_path
        else:
            print('ignore', f'"{self.path}"')
            response_code = 400

        db.close()

        if not send_file_path:
            if response_code in (200, 304) and reply is None:
                reply = OK_REPLY
            if response_code == 400:
                reply = INVALID_REQUEST_REPLY
            elif response_code == 404:
                reply = NOT_FOUND_REPLY

            if isinstance(reply, (dict, list)):
                reply = json.dumps(reply)
                content_type = "text/json"

            if isinstance(reply, str):
                reply = bytes(reply, "utf-8")

        if content_type is None:
            cache_control = "no-store"

        self.protocol_version = 'HTTP/1.1'

        self.send_response(response_code)

        self.send_header("Content-type", content_type)
        if cache_control is not None:
            self.send_header("Cache-Control", cache_control)
        if last_modified is not None:
            # self.date_time_string
            self.send_header("Last-Modified", epoch_to_httptime(last_modified))
        if etag is not None:
            self.send_header("ETag", f'"{etag}"')

        # should be null?
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

        # print(self.headers)

        if send_file_path is not None:
            self.send_file(send_file_path)
        else:
            try:
                self.wfile.write(reply)
            except Exception as e:
                print('handler.wfile.write(reply) FAIL!!!!', e)

    def send_file(self, file_path):
        import time

        is_tmp = self.path.startswith("/tmp/")

        CHUNK_SIZE = 1024 * 1024 * 1  # 1 MiB
        with open(file_path, "rb") as f:
            while True:
                chunk = f.read(CHUNK_SIZE)

                if not chunk:
                    break
                else:
                    try:
                        self.wfile.write(chunk)

                    except ConnectionResetError as e:
                        print('handler.send_file ConnectionResetError', e)

                        break
                    except IOError as e:
                        print('handler.send_file IOError', e)

                        break
                    except Exception as e:
                        print('handler.send_file Unknow Exception', e)

                        break
                    finally:
                        del chunk

                if is_tmp:
                    # allow transcoder to catch up
                    time.sleep(1.5)


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
    httpd = socketserver.ThreadingTCPServer((hostName, serverPort), Handler)
except OSError:
    print('skip', serverPort)
    for port in range(8087, 8097):
        serverPort = port
        try:
            httpd = socketserver.ThreadingTCPServer(
                (hostName, serverPort), Handler
            )
            break
        except OSError:
            print('skip', serverPort)

print(f"Server started http://{hostName}:{serverPort}")
try:
    httpd.daemon_threads = True
    subprocess.Popen([
        'firefox',
        # 'chromium',
        # f'file:///data/tmp/Media%20Server/html/index.html?api_url=http://{hostName}:{serverPort}'
        f'http://{hostName}:{serverPort}'
    ])
    httpd.serve_forever()
except KeyboardInterrupt:
    pass

finally:
    httpd.server_close()
    print("Server stopped.")

    from classes.streaming import TMP_FOLDER as TMP_FOLDER_PATH
    import multiprocessing
    import time

    for process in [p for p in multiprocessing.active_children() if (
        p.name.startswith(TMP_FOLDER_PATH)
    )]:
        print(f'Stopping {process}')
        process.terminate()
        time.sleep(1)
        process.close()
        multiprocessing.active_children()

    for f in os.listdir(TMP_FOLDER_PATH):
        print(f'removing {f}')
        os.remove(os.path.join(TMP_FOLDER_PATH, f))
