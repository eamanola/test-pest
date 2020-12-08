import socketserver
import os
import re
from db.db import get_db


class RequestHandler(socketserver.StreamRequestHandler):

    NOT_FOUND_REPLY = {'code': 404, 'message': 'Not found'}
    INVALID_REQUEST_REPLY = {'code': 400, 'message': 'Invalid request'}
    OK_REPLY = {'code': 200, 'message': 'Ok'}
    CACHE_ONE_WEEK = f"private, max-age={7 * 24 * 60 * 60}"
    MUST_REVALIDATE = "private, must-revalidate, max-age=0"
    MAX_BYTES_PER_CHUNK_CONN = 1024 * 1024 * 8
    CMD_CHUNK_SIZE = 1024 * 8
    FILE_CHUNK_SIZE = CMD_CHUNK_SIZE  # 1024 * 1024 * 1

    def epoch_to_httptime(self, secs):
        from datetime import datetime, timezone

        dt = datetime.fromtimestamp(secs, timezone.utc)

        return dt.strftime('%a, %d %b %Y %H:%M:%S GMT')

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

    def mime_type(self, file_name):
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
        elif file_name.endswith("h264"):
            content_type = 'video/mp4; codecs="avc1.42E01E"'
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
        elif file_name.endswith(".aac"):
            content_type = "audio/aac"
        elif file_name.endswith(".flac"):
            content_type = "audio/flac"
        elif file_name.endswith(".vorbis"):
            content_type = 'audio/ogg; codecs="vorbis"'
        else:
            content_type = "application/octet-stream"

        return content_type

    def send_response(self, response_code):
        self.header_str = f"{self.protocol_version} {str(response_code)}\r\n"

    def send_header(self, key, value):
        self.header_str = f"{self.header_str}{key}: {str(value)}\r\n"

    def end_headers(self):
        self.header_str = f"{self.header_str}\r\n"

        for entry in self.header_str.split("\r\n"):
            print(entry, self.path)
            break

        self.wfile.write(bytes(self.header_str, "utf8"))
        self.wfile.flush()

    def router(self, db, request):
        print('ignore', self.path)
        return None

    def do_GET(self):
        response_code, response_headers = None, {}
        response_json, response_file_path, response_cmd = None, None, None

        try:
            db = get_db()
            db.connect()

            import urllib.parse
            parsed = urllib.parse.urlparse(self.path)

            request = {
                "api_params": parsed.path[1:].split("/"),
                "optional_params": urllib.parse.parse_qs(parsed.query)
            }

            response = self.router(db, request)

        finally:
            db.close()

        if response is not None:
            if "code" in response.keys():
                response_code = response["code"]
            if "headers" in response.keys():
                response_headers = {**response_headers, **response["headers"]}
            if "json" in response.keys():
                response_json = response["json"]
            if "file_path" in response.keys():
                response_file_path = response["file_path"]
            if "cmd" in response.keys():
                response_cmd = response["cmd"]

        else:
            response_code = 400

        if response_code is None:
            raise Exception("no response code for:", self.path)

        if (
            response_cmd is None
            and response_file_path is None
            and response_json is None
        ):
            if response_code in (200, 304):
                response_json = self.OK_REPLY
            elif response_code == 400:
                response_json = self.INVALID_REQUEST_REPLY
            elif response_code == 404:
                response_json = self.NOT_FOUND_REPLY

        if "Content-type" not in response_headers.keys():
            if response_json is not None:
                response_headers["Content-type"] = "text/json"
            elif response_file_path is not None:
                response_headers["Content-type"] = self.mime_type(
                    response_file_path
                )

        if "Cache-Control" not in response_headers.keys():
            if (
                "ETag" in response_headers.keys()
                or "Last-Modified" in response_headers.keys()
            ):
                response_headers["Cache-Control"] = self.MUST_REVALIDATE

        if response_file_path is not None:
            response_headers["Transfer-Encoding"] = "chunked"
            response_headers["Accept-Ranges"] = "bytes"

            MAX_SIZE = self.MAX_BYTES_PER_CHUNK_CONN
            file_size = os.path.getsize(response_file_path)
            if MAX_SIZE < file_size:
                response_headers["Content-Length"] = MAX_SIZE
            else:
                response_headers["Content-Length"] = file_size

            if 'Range' in self.headers and response_code == 200:
                response_code = 206

                # print('r:', self.headers["Range"], self.path)

                start = re.compile(r'^bytes=(\d+)-').search(
                    self.headers['Range']
                )
                if start:
                    start_1 = int(start.group(1))
                    if MAX_SIZE < file_size - start_1:
                        response_headers["Content-Length"] = MAX_SIZE
                    else:
                        response_headers["Content-Length"] = (
                            file_size - start_1
                        )

                    if start_1 + MAX_SIZE < file_size:
                        end = start_1 + MAX_SIZE
                    else:
                        end = file_size

                    response_headers["Content-Range"] = (
                        f"bytes {start_1}-{end}/{file_size}"
                    )
                    print('cr:', response_headers["Content-Range"], self.path)

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
                import json
                self.send_body(bytes(json.dumps(response_json), "utf-8"))

        except (ConnectionResetError, IOError, Exception) as e:
            print('Send error:', e, self.path)

    def send_body(self, body):
        self.wfile.write(body)
        self.wfile.flush()

    def send_chunks(self, file_path):
        NEW_LINE = bytes("\r\n", "utf-8")
        MAX_SIZE = self.MAX_BYTES_PER_CHUNK_CONN
        CHUNK_SIZE = self.FILE_CHUNK_SIZE  # 1024 * 1024 * 1

        with open(file_path, "rb") as f:
            if 'Range' in self.headers:
                start = re.compile(r'^bytes=(\d+)-').search(
                    self.headers['Range']
                )
                if start:
                    f.seek(int(start.group(1)), 0)

            sent = 0
            while sent < MAX_SIZE:
                chunk = f.read(CHUNK_SIZE)
                if not chunk:
                    break

                try:
                    chunk_len = len(chunk)
                    sent = sent + chunk_len
                    post = (
                        bytes(hex(chunk_len)[2:], "utf-8") + NEW_LINE
                        + chunk + NEW_LINE
                    )
                    if chunk_len < CHUNK_SIZE or sent >= MAX_SIZE:
                        post = (
                            post + bytes("0", "utf-8") + NEW_LINE + NEW_LINE
                        )

                    self.wfile.write(post)
                    self.wfile.flush()

                    # print(sent, '/', MAX_SIZE, self.path)

                finally:
                    del chunk
                    del post

    def send_cmd_output(self, cmd):
        try:
            import subprocess
            import time
            proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)

            CHUNK_SIZE = self.CMD_CHUNK_SIZE

            chunk = proc.stdout.read(CHUNK_SIZE)
            while chunk:
                len_chunk = len(chunk)
                if len_chunk < CHUNK_SIZE:
                    time.sleep(1)
                del len_chunk

                self.wfile.write(chunk)
                self.wfile.flush()
                del chunk

                chunk = proc.stdout.read(CHUNK_SIZE)

        finally:
            proc.kill()
            print('Close', self.path)

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
        if self.path in ("/", ""):
            self.path = "/index.html"

        self.headers = {}
        if len(data) > 1:
            re_header = re.compile("^([^:]+): (.*)$")
            for i in range(1, len(data)):
                parts = re_header.search(data[i])
                self.headers[parts.group(1).strip()] = parts.group(2).strip()

        try:
            self.do_GET()

        finally:
            self.wfile.flush()
            self.wfile.close()