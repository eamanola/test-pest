import os
import sys
from api.apirequesthandler import ApiRequestHandler


class FileRequestHandler(ApiRequestHandler):

    def image(self, db, request):
        code, headers, file_path = 404, {}, None

        image_path = os.sep.join([sys.path[0]] + self.path[1:].split("/"))

        if os.path.exists(image_path):
            code = 200
            headers["Cache-Control"] = self.CACHE_ONE_WEEK
            file_path = image_path

        return {"code": code, "headers": headers, "file_path": file_path}

    def webclient(self, db, request):
        code, headers, file_path = None, {}, None
        client_file_path = os.path.join(
            sys.path[0],
            "reference-ui",
            "web",
            os.sep.join(self.path[1:].split("/"))
        )

        code = self.revalidate_client_cache(file_path=client_file_path)

        if code is None:
            if os.path.exists(client_file_path):
                code = 200
                if self.path.startswith("/images/"):
                    headers["Cache-Control"] = self.CACHE_ONE_WEEK
                else:
                    headers["Last-Modified"] = self.epoch_to_httptime(
                        os.path.getmtime(client_file_path)
                    )
                file_path = client_file_path
            else:
                code = 404

        return {"code": code, "headers": headers, "file_path": file_path}

    def router(self, db, request):
        response = None

        if ((
            self.path.startswith("/images/thumbnails/")
            and self.path.endswith(".png")
        ) or (
            self.path.startswith("/images/posters/")
            and self.path.endswith(".jpg")
        )):
            response = self.image(db, request)

        elif (
            self.path in (
                "/images/count-down.gif",
                "/images/loading.gif",
                "/images/play-icon.png",
                "/scripts/keyboard.js",
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
            response = self.webclient(db, request)

        return super().router(db, request) if response is None else response
