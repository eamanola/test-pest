import socketserver
import subprocess
import json
import api.scripts as api
from api.to_dict import DictContainer, DictMedia
from db.db import get_db
import os
import sys
import time
from CONFIG import CHOSTNAME, CPORT, CTMP_DIR

NOT_FOUND_REPLY = {'code': 404, 'message': 'Not found'}
INVALID_REQUEST_REPLY = {'code': 400, 'message': 'Invalid request'}
OK_REPLY = {'code': 200, 'message': 'Ok'}
MUST_REVALIDATE = "private, must-revalidate, max-age=0"
CACHE_ONE_WEEK = f"private, max-age={7 * 24 * 60 * 60}"


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
    elif file_name.endswith(".ass"):
        content_type = "text/ass"
    elif file_name.endswith(".webm"):
        content_type = "video/webm"
    elif file_name.endswith(".mkv"):
        content_type = "video/x-matroska"
    elif file_name.endswith(".mp4"):
        content_type = "video/mp4"
    elif file_name.endswith(".opus"):
        content_type = "audio/opus"
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
    else:
        content_type = "application/octet-stream"

    return content_type


class Handler(socketserver.StreamRequestHandler):

    def revalidate_client_cache(self, file_path=None):
        response_code = None

        if 'If-None-Match' in self.headers.keys():
            if file_path is not None:
                from hashlib import sha256

                with open(file_path, "rb") as f:
                    _bytes = f.read()

                etag = sha256(_bytes).hexdigest()
            else:
                etag = get_db().version()

            if f'"{etag}"' == self.headers['If-None-Match']:
                response_code = 304

        elif 'If-Modified-Since' in self.headers.keys():
            from datetime import datetime, timezone

            if file_path is not None:
                last_modified = int(os.path.getmtime(file_path))
            else:
                last_modified = get_db().last_modified()

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
        response_code = None

        response_headers = {}

        response_json = None
        response_file_path = None
        response_cmd = None

        db = get_db()
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
                response_headers["ETag"] = db.version()
                response_json = {
                    'play_next_list':  [DictMedia.dict(m) for m in play_next],
                    'media_libraries':
                        [DictContainer.dict(ml) for ml in media_libraries]
                }

        elif self.path.startswith("/c/"):
            response_code = self.revalidate_client_cache()

            if response_code is None:
                parts = self.path[1:].split("/")
                item_id = parts[-1]

                if item_id and len(parts) == 2:
                    container = api.get_container(db, item_id)

                    if container:
                        response_code = 200
                        response_headers["ETag"] = db.version()
                        response_json = DictContainer.dict(container)
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
                        response_headers["ETag"] = db.version()
                        response_json = DictMedia.dict(media)
                    else:
                        response_code = 404
                else:
                    response_code = 400

        elif self.path.startswith("/playnextlist"):
            response_code = self.revalidate_client_cache()

            if response_code is None:
                play_next_list = api.play_next_list(db)

                response_code = 200
                response_headers["ETag"] = db.version()
                response_json = [DictMedia.dict(m) for m in play_next_list]

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
                    response_json = DictContainer.dict(
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
                    response_json = {'identified': identified}
                    if identified:
                        response_json = {**response_json, **item_dict}
                    else:
                        response_json = {**response_json, 'data_id': item_id}
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
                    response_json = {**message, 'data_id': item_id}
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
                    response_json = item_dict
                else:
                    response_code = 404
            else:
                response_code = 400

        elif self.path.startswith("/addmedialibrary/"):
            print(self.path)

            media_library_param = self.path.replace("/addmedialibrary/", "")
            if media_library_param:
                from urllib.parse import unquote
                media_library_path = unquote(media_library_param)

                if api.add_media_library(db, media_library_path):
                    response_code = 200
                else:
                    response_code = 404
            else:
                response_code = 400

        elif self.path.startswith("/streams/"):
            import urllib.parse
            parsed = urllib.parse.urlparse(self.path)

            parts = parsed.path[1:].split("/")
            codec = parts[1]
            width = int(parts[2])
            height = int(parts[3])
            media_id = parts[4]

            params = urllib.parse.parse_qs(parsed.query)
            start_time = (
                int(params['start'][0]) if "start" in params.keys() else 0
            )

            if (media_id and codec and width and height and len(parts) == 5):
                streams = api.get_streams(
                    db,
                    media_id,
                    codec,
                    width,
                    height,
                    start_time
                )
                if streams:
                    response_code = 200
                    response_json = streams
                else:
                    response_code = 404
            else:
                response_code = 400

        elif self.path.startswith("/video/"):
            import urllib.parse
            parsed = urllib.parse.urlparse(self.path)

            parts = parsed.path[1:].split("/")
            codec = parts[1]
            width = int(parts[2])
            height = int(parts[3])
            media_id = parts[4]

            params = urllib.parse.parse_qs(parsed.query)
            transcode = (
                "transcode" in params.keys()
                and params['transcode'][0] == '1'
            )
            start_time = (
                int(params['start'][0]) if "start" in params.keys() else 0
            )
            subtitle_index = (
                int(params['si'][0]) if "si" in params.keys() else None
            )

            if (media_id and codec and width and height and len(parts) == 5):
                stream = api.get_video_stream(
                    db,
                    media_id,
                    codec,
                    width,
                    height,
                    transcode,
                    start_time,
                    subtitle_index
                )
                if stream:
                    response_code = 200
                    response_headers["Cache-Control"] = CACHE_ONE_WEEK
                    if transcode:
                        response_headers["Content-type"] = mime_type(".webm")
                        response_cmd = stream
                    else:
                        response_file_path = stream
                else:
                    response_code = 404
            else:
                response_code = 400

        elif self.path.startswith("/audio/"):
            import urllib.parse
            parsed = urllib.parse.urlparse(self.path)

            parts = parsed.path[1:].split("/")
            stream_index = parts[1]
            media_id = parts[2]

            params = urllib.parse.parse_qs(parsed.query)
            start_time = (
                int(params['start'][0]) if "start" in params.keys() else 0
            )

            if (media_id and stream_index and len(parts) == 3):
                cmd = api.get_audio_stream(
                    db,
                    media_id,
                    stream_index,
                    start_time
                )
                if cmd:
                    response_code = 200
                    response_headers["Cache-Control"] = CACHE_ONE_WEEK
                    response_headers["Content-type"] = mime_type(".opus")

                    response_cmd = cmd
                else:
                    response_code = 404
            else:
                response_code = 400

        elif self.path.startswith("/subtitle/"):
            parts = self.path[1:].split("/")
            type = parts[1]
            stream_index = parts[2]
            media_id = parts[3].split(".")[0]
            is_bitmap = parts[3].split(".")[1] == "tra"

            if (
                media_id
                and type
                and stream_index
                and len(parts) == 4
                and not is_bitmap
            ):
                cmd, mime = api.get_subtitle(
                    db,
                    media_id,
                    type,
                    stream_index
                )
                if cmd:
                    response_code = 200
                    response_headers["Cache-Control"] = CACHE_ONE_WEEK
                    response_headers["Content-type"] = mime_type(mime)

                    response_cmd = cmd
                else:
                    response_code = 404
            else:
                response_code = 400

        elif self.path.startswith("/fonts/"):
            parts = self.path[1:].split("/")
            media_id = parts[1]
            font_name = parts[2]

            if (media_id and font_name and len(parts) == 3):
                font_path = api.get_font(db, media_id, font_name)

                if font_path:
                    response_code = 200
                    response_headers["Cache-Control"] = CACHE_ONE_WEEK
                    response_file_path = font_path
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
        ):
            response_code = 404

            path = [sys.path[0]] + self.path[1:].split("/")

            file_path = os.sep.join(path)

            if os.path.exists(file_path):
                response_code = 200
                response_headers["Cache-Control"] = CACHE_ONE_WEEK
                response_file_path = file_path

        elif (
            self.path in (
                "/images/count-down.gif",
                "/images/loading.gif",
                "/images/play-icon.png",
                "/scripts/page_builder.js",
                "/scripts/player.js",
                "/scripts/scripts.js",
                "/styles/styles.css",
                "/styles/fonts/FONTIN_SANS_0.OTF",
                "/index.html"
            )
            or self.path in (
                "/scripts/octopus-ass/subtitles-octopus-worker-legacy.data",
                "/scripts/octopus-ass/subtitles-octopus-worker-legacy.js",
                "/scripts/octopus-ass/subtitles-octopus-worker-legacy.js.mem",
                "/scripts/octopus-ass/subtitles-octopus-worker.data",
                "/scripts/octopus-ass/subtitles-octopus-worker.js",
                "/scripts/octopus-ass/subtitles-octopus-worker.wasm",
                "/scripts/octopus-ass/subtitles-octopus.js"
            )
        ):
            file_path = os.path.join(
                sys.path[0],
                "html",
                os.sep.join(self.path[1:].split("/"))
            )

            response_code = self.revalidate_client_cache(file_path=file_path)

            if response_code is None:
                if os.path.exists(file_path):
                    response_code = 200
                    if self.path.startswith("/images/"):
                        response_headers["Cache-Control"] = CACHE_ONE_WEEK
                    else:
                        response_headers["Last-Modified"] = epoch_to_httptime(
                            os.path.getmtime(file_path)
                        )

                    response_file_path = file_path
                else:
                    response_code = 404
        else:
            print('ignore', f'"{self.path}"')
            response_code = 400

        db.close()

        if response_code is None:
            raise Exception("no response code for:", self.path)

        if not response_cmd and not response_file_path and not response_json:
            if response_code in (200, 304):
                response_json = OK_REPLY
            elif response_code == 400:
                response_json = INVALID_REQUEST_REPLY
            elif response_code == 404:
                response_json = NOT_FOUND_REPLY

        if "Content-type" not in response_headers.keys():
            if response_json is not None:
                response_headers["Content-type"] = "text/json"
            elif response_file_path is not None:
                response_headers["Content-type"] = mime_type(
                    response_file_path
                )

        if "Cache-Control" not in response_headers.keys():
            if (
                "ETag" in response_headers.keys()
                or "Last-Modified" in response_headers.keys()
            ):
                response_headers["Cache-Control"] = MUST_REVALIDATE

        if response_file_path is not None:
            response_headers["Transfer-Encoding"] = "chunked"

        # should be null?
        response_headers["Access-Control-Allow-Origin"] = "*"

        self.protocol_version = 'HTTP/1.1'

        try:
            self.send_response(response_code)

            for key in response_headers.keys():
                self.send_header(key, response_headers[key])
            self.end_headers()

            if response_cmd:
                self.send_cmd_output(response_cmd)

            elif response_file_path:
                self.send_chunks(response_file_path)

            elif response_json is not None:
                self.send_body(bytes(json.dumps(response_json), "utf-8"))

        except (ConnectionResetError, IOError, Exception) as e:
            print('Send error:', e)

    def send_cmd_output(self, cmd):
        try:
            print('start', self.path)
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)

            CHUNK_SIZE = 1024 * 8  # io.DEFAULT_BUFFER_SIZE

            chunk = proc.stdout.read(CHUNK_SIZE)
            while chunk:
                len_chunk = len(chunk)
                if len_chunk < CHUNK_SIZE:
                    print('sleep', self.path)
                    time.sleep(1)
                del len_chunk

                self.wfile.write(chunk)
                del chunk

                chunk = proc.stdout.read(CHUNK_SIZE)

        finally:
            proc.kill()
            print('Close', self.path)

    def send_chunks(self, file_path):
        NEW_LINE = bytes("\r\n", "utf-8")
        CHUNK_SIZE = 1024 * 1024 * 1

        with open(file_path, "rb") as f:
            while True:
                chunk = f.read(CHUNK_SIZE)

                if not chunk:
                    break

                try:
                    chunk_len = len(chunk)
                    post = (
                        bytes(hex(chunk_len)[2:], "utf-8") + NEW_LINE
                        + chunk + NEW_LINE
                    )
                    if chunk_len < CHUNK_SIZE:
                        post = (
                            post + bytes("0", "utf-8") + NEW_LINE + NEW_LINE
                        )

                    self.wfile.write(post)
                    self.wfile.flush()

                finally:
                    del chunk
                    del post

    def send_body(self, body):
        self.wfile.write(body)

    def send_response(self, response_code):
        self.header_str = f"{self.protocol_version} {str(response_code)}\r\n"

    def send_header(self, key, value):
        self.header_str = f"{self.header_str}{key}: {str(value)}\r\n"

    def end_headers(self):
        self.header_str = f"{self.header_str}\r\n"

        for entry in self.header_str.split("\r\n"):
            print(entry, self.path)
            break
        print("")

        self.wfile.write(bytes(self.header_str, "utf8"))
        self.wfile.flush()

    def handle(self):
        data = self.request.recv(1024).strip().decode("utf8")

        if data == "":
            print('Nothing to do')
            return

        else:
            data = data.split("\r\n")

        for entry in data:
            print(entry)
            break

        self.path = data[0].split(" ")[1]

        self.headers = {}
        if len(data) > 1:
            import re
            re_header = re.compile("^([^:]+): (.*)$")
            for i in range(1, len(data)):
                parts = re_header.search(data[i])
                self.headers[parts.group(1).strip()] = parts.group(2).strip()

        try:
            self.do_GET()

        finally:
            self.wfile.flush()
            self.wfile.close()


hostName = CHOSTNAME
serverPort = CPORT
socketserver.ThreadingTCPServer.allow_reuse_address = True
httpd = socketserver.ThreadingTCPServer((hostName, serverPort), Handler)

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

    import shutil
    if os.path.exists(CTMP_DIR):
        shutil.rmtree(CTMP_DIR)

sys.exit(0)
