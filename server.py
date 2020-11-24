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
        reply = None
        send_file_path = None
        cache_control = None
        last_modified = None
        etag = None
        stream_cmd = None

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
                    reply = streams
                    response_code = 200
                else:
                    response_code = 404

            else:
                response_code = 400

        elif self.path.startswith("/video/"):
            print(self.path)
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
                    # "private, must-revalidate, max-age=0"
                    cache_control = "private, max-age=604800"
                    if transcode:
                        content_type = mime_type(".webm")
                        stream_cmd = stream
                    else:
                        content_type = mime_type(stream)
                        send_file_path = stream
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
                    content_type = mime_type(".opus")
                    # "private, must-revalidate, max-age=0"
                    cache_control = "private, max-age=604800"

                    stream_cmd = cmd
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
                subtitle_path = api.get_subtitle(
                    db,
                    media_id,
                    type,
                    stream_index
                )
                if subtitle_path:
                    response_code = 200
                    send_file_path = subtitle_path
                    content_type = mime_type(subtitle_path)
                    cache_control = "private, max-age=604800"
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
                    send_file_path = font_path
                    content_type = mime_type(font_path)
                    cache_control = "private, max-age=604800"
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
            content_type = None

            path = [sys.path[0]] + self.path[1:].split("/")

            file_path = os.sep.join(path)

            if os.path.exists(file_path):
                response_code = 200
                send_file_path = file_path

                content_type = mime_type(file_path)

                cache_control = "private, max-age=604800"

        elif (
            self.path in (
                "/images/count-down.gif",
                "/images/loading.gif",
                "/images/play-icon.png",
                "/scripts/page_builder.js",
                "/scripts/player.js",
                "/scripts/scripts.js",
                "/styles/styles.css",
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
                    send_file_path = file_path

                    content_type = mime_type(file_path)

                    cache_control = "private, must-revalidate, max-age=0"

                    if content_type.startswith("image"):
                        cache_control = "private, max-age=604800"

                    last_modified = os.path.getmtime(file_path)

                else:
                    response_code = 404
        else:
            print('ignore', f'"{self.path}"')
            response_code = 400

        db.close()

        if not send_file_path and not stream_cmd:
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
        if send_file_path is not None:
            self.send_header("Transfer-Encoding", "chunked")

        # should be null?
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

        # print(self.headers)

        try:
            if stream_cmd:
                self.send_cmd_output(stream_cmd)

            elif send_file_path:
                self.send_chunks(send_file_path)

            else:
                self.wfile.write(reply)

        except (ConnectionResetError, IOError, Exception) as e:
            print('Send error:', e)

        finally:
            self.wfile.flush()
            self.wfile.close()

    def send_cmd_output(self, cmd):
        try:
            print('cmd:', ' '.join(cmd))
            proc = subprocess.Popen(cmd, stdout=self.wfile)
            proc.wait()

        finally:
            proc.terminate()
            time.sleep(1)

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
                        bytes(hex(chunk_len)[2:], "utf-8")
                        + NEW_LINE
                        + chunk
                        + NEW_LINE
                    )
                    if chunk_len < CHUNK_SIZE:
                        post = (
                            post
                            + bytes("0", "utf-8")
                            + NEW_LINE
                            + NEW_LINE
                        )

                    self.wfile.write(post)

                finally:
                    del chunk

    def send_response(self, response_code):
        self.header_str = f"{self.protocol_version} {str(response_code)}\r\n"

    def send_header(self, key, value):
        self.header_str = f"{self.header_str}{key}: {str(value)}\r\n"

    def end_headers(self):
        self.header_str = f"{self.header_str}\r\n"

        for entry in self.header_str.split("\r\n"):
            print(self.path, entry)
            break
        print("")

        self.wfile.write(bytes(self.header_str, "utf8"))

    def handle(self):
        data = self.request.recv(1024).strip().decode("utf8").split("\r\n")

        for entry in data:
            print(entry)
            break

        try:
            self.path = data[0].split(" ")[1]
        except Exception as e:
            print('RECV', e)
            for entry in data:
                print(entry)
            print("")

        self.headers = {}
        import re
        re_header = re.compile("^([^:]+): (.*)")
        for i in range(1, len(data)):
            parts = re_header.search(data[i])
            self.headers[parts.group(1).strip()] = parts.group(2).strip()

        self.do_GET()


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
