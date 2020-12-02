from api.filerequesthandler import FileRequestHandler
import api.scripts as api  # should go streaming directly?


class StreamingRequestHandler(FileRequestHandler):

    def streams(self, db, request):
        code, json = 400, None
        api_params, params = request["api_params"], request["optional_params"]

        width = int(api_params[1])
        height = int(api_params[2])
        media_id = api_params[3]

        decoders = (
            params['decoders'] if "decoders" in params.keys() else []
        )
        start_time = (
            int(params['start'][0]) if "start" in params.keys() else 0
        )

        if (media_id and width and height and len(api_params) == 4):
            streams = api.get_streams(
                db, media_id, width, height, decoders, start_time
            )
            if streams:
                code = 200
                json = streams
            else:
                code = 404

        return {"code": code, "json": json}

    def video(self, db, request):
        code, headers, file_path, cmd = 400, {}, None, None
        api_params, params = request["api_params"], request["optional_params"]

        width = int(api_params[1])
        height = int(api_params[2])
        media_id = api_params[3]

        if "transcode" in params.keys():
            transcode = params['transcode'][0]
        else:
            transcode = None

        start_time = (
            int(params['start'][0]) if "start" in params.keys() else 0
        )
        subtitle_index = (
            int(params['si'][0]) if "si" in params.keys() else None
        )

        if (media_id and width and height and len(api_params) == 4):
            stream, mime = api.get_video_stream(
                db, media_id, width, height,
                transcode, start_time, subtitle_index
            )
            if stream:
                code = 200

                headers["Content-type"] = self.mime_type(mime)

                if isinstance(stream, str):
                    file_path = stream
                    headers["Cache-Control"] = self.CACHE_ONE_WEEK
                else:
                    cmd = stream
                    headers["Cache-Control"] = self.MUST_REVALIDATE
            else:
                code = 404

        return {
            "code": code,
            "headers": headers,
            "file_path": file_path,
            "cmd": cmd
        }

    def audio(self, db, request):
        code, headers, file_path, cmd = 400, {}, None, None
        api_params, params = request["api_params"], request["optional_params"]

        stream_index = api_params[1]
        media_id = api_params[2]

        start_time = (
            int(params['start'][0]) if "start" in params.keys() else 0
        )

        if "transcode" in params.keys():
            transcode = params['transcode'][0]
        else:
            transcode = None

        if (media_id and stream_index and len(api_params) == 3):
            stream, mime = api.get_audio_stream(
                db, media_id, stream_index, transcode, start_time
            )
            if stream:
                code = 200
                headers["Content-type"] = self.mime_type(mime)

                if isinstance(stream, str):
                    file_path = stream
                    headers["Cache-Control"] = self.CACHE_ONE_WEEK
                else:
                    cmd = stream
                    self.headers["Cache-Control"] = MUST_REVALIDATE
            else:
                code = 404

        return {
            "code": code,
            "headers": headers,
            "file_path": file_path,
            "cmd": cmd
        }

    def subtitle(self, db, request):
        code, headers, cmd = 400, {}, None
        api_params, params = request["api_params"], request["optional_params"]

        type = api_params[1]
        stream_index = api_params[2]
        media_id = api_params[3].split(".")[0]
        is_bitmap = api_params[3].split(".")[1] == "tra"

        start_time = (
            int(params['start'][0]) if "start" in params.keys() else 0
        )

        if (
            media_id
            and type
            and stream_index
            and len(api_params) == 4
            and not is_bitmap
        ):
            stream, mime = api.get_subtitle(
                db, media_id, type, stream_index, start_time
            )
            if stream:
                code = 200
                headers["Cache-Control"] = self.CACHE_ONE_WEEK
                headers["Content-type"] = self.mime_type(mime)

                cmd = stream
            else:
                code = 404

        return {"code": code, "headers": headers, "cmd": cmd}

    def fonts(self, db, request):
        code, headers, file_path = 400, {}, None
        api_params = request["api_params"]

        api_params = self.path[1:].split("/")
        media_id = api_params[1]
        font_name = api_params[2]

        if (media_id and font_name and len(api_params) == 3):
            font_path = api.get_font(db, media_id, font_name)

            if font_path:
                code = 200
                headers["Cache-Control"] = self.CACHE_ONE_WEEK
                file_path = font_path
            else:
                code = 404

        return {"code": code, "headers": headers, "file_path": file_path}

    def router(self, db, request):
        response = None

        if self.path.startswith("/streams/"):
            response = self.streams(db, request)

        elif self.path.startswith("/video/"):
            response = self.video(db, request)

        elif self.path.startswith("/audio/"):
            response = self.audio(db, request)

        elif self.path.startswith("/subtitle/"):
            response = self.subtitle(db, request)

        elif self.path.startswith("/fonts/"):
            response = self.fonts(db, request)

        return super().router(db, request) if response is None else response
