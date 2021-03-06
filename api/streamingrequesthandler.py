from api.filerequesthandler import FileRequestHandler
import api.scripts as api  # should go streaming directly?


class StreamingRequestHandler(FileRequestHandler):

    def streams(self, db, request):
        code, json = 400, None
        api_params, params = request["api_params"], request["optional_params"]

        media_id = api_params[1]

        if media_id:
            streams = api.get_streams(db, media_id)
            if streams:
                code = 200
                json = streams
            else:
                code = 404

        return {"code": code, "json": json}

    def av(self, db, request):
        code, headers, file_path, redirect, cmd = 400, {}, None, None, None
        input_cmd = None
        api_params, params = request["api_params"], request["optional_params"]

        media_id = api_params[1]

        video_index = (
            int(params['v'][0]) if "v" in params.keys() else None
        )
        audio_index = (
            int(params['a'][0]) if "a" in params.keys() else None
        )
        vcodec = (
            params['cv'][0] if "cv" in params.keys() else None
        )
        acodec = (
            params['ca'][0] if "ca" in params.keys() else None
        )
        start_time = (
            float(params['start'][0]) if "start" in params.keys() else None
        )
        width = (
            int(params['w'][0]) if "w" in params.keys() else None
        )
        height = (
            int(params['h'][0]) if "h" in params.keys() else None
        )
        subtitle_index = (
            int(params['s'][0]) if "s" in params.keys() else None
        )

        disable_re = request["client"] in ("Web0S",)

        stream, mime, input_cmd = api.av(
            db, media_id, video_index, vcodec, audio_index, acodec,
            start_time, width, height, subtitle_index, disable_re
        )

        if stream:
            code = 200

            if isinstance(stream, str):
                if stream.startswith("http"):
                    code = 302
                    redirect = stream
                else:
                    file_path = stream
                    headers["Cache-Control"] = self.CACHE_ONE_WEEK
            else:
                cmd = stream
                headers["Content-type"] = self.mime_type(mime)
                headers["Cache-Control"] = self.MUST_REVALIDATE
        else:
            code = 404

        return {
            "code": code,
            "headers": headers,
            "redirect": redirect,
            "file_path": file_path,
            "cmd": cmd,
            "input_cmd": input_cmd
        }

    def subtitle(self, db, request):
        code, headers, cmd = 400, {}, None
        api_params, params = request["api_params"], request["optional_params"]

        type = api_params[1]
        stream_index = api_params[2]
        parts = api_params[3].split(".")
        media_id = parts[0]
        format = parts[1]
        is_bitmap = format == "tra"

        start_time = (
            float(params['start'][0]) if "start" in params.keys() else 0
        )

        if (
            media_id
            and type
            and stream_index
            and len(api_params) == 4
            and not is_bitmap
        ):
            stream, mime = api.get_subtitle(
                db, media_id, type, stream_index, format, start_time
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

        from urllib.parse import unquote
        font_name = unquote(api_params[2])

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

        elif self.path.startswith("/subtitle/"):
            response = self.subtitle(db, request)

        elif self.path.startswith("/fonts/"):
            response = self.fonts(db, request)

        elif self.path.startswith("/av/"):
            response = self.av(db, request)

        return super().router(db, request) if response is None else response
