import api.scripts as api
from api.to_dict import DictContainer, DictMedia
from api.requesthandler import RequestHandler


class ApiRequestHandler(RequestHandler):

    def frontpage(self, db, request):
        code, headers, json = None, {}, None
        code = self.revalidate_client_cache()

        if code is None:
            media_library_ids = api.get_media_libraries(db)

            media_libraries = []
            for media_library_id in media_library_ids:
                media_libraries.append(api.get_container(db, media_library_id))

            # temp
            for media_library in media_libraries:
                if media_library.title() == "/data/viihde/anime/":
                    break
            media_libraries.remove(media_library)
            media_libraries.insert(0, media_library)

            play_next = api.play_next_list(db)
            code = 200
            headers["ETag"] = db.version()
            json = {
                'play_next_list':  [DictMedia.dict(m) for m in play_next],
                'media_libraries':
                    [DictContainer.dict(ml) for ml in media_libraries]
            }

        return {"code": code, "headers": headers, "json": json}

    def container(self, db, request):
        code, headers, json = None, {}, None
        code = self.revalidate_client_cache()

        if code is None:
            api_params = request["api_params"]
            item_id = api_params[-1]

            if item_id and len(api_params) == 2:
                container = api.get_container(db, item_id)

                if container:
                    code = 200
                    headers["ETag"] = db.version()
                    json = DictContainer.dict(container)
                else:
                    code = 404
            else:
                code = 400

        return {"code": code, "headers": headers, "json": json}

    def media(self, db, request):
        code, headers, json = None, {}, None
        code = self.revalidate_client_cache()

        if code is None:
            api_params = request["api_params"]
            item_id = api_params[-1]

            if item_id and len(api_params) == 2:
                media = api.get_media(db, item_id)

                if media:
                    code = 200
                    headers["ETag"] = db.version()
                    json = DictMedia.dict(media)
                else:
                    code = 404
            else:
                code = 400

        return {"code": code, "headers": headers, "json": json}

    def playnextlist(self, db, request):
        code, headers, json = None, {}, None
        code = self.revalidate_client_cache()

        if code is None:
            play_next_list = api.play_next_list(db)

            code = 200
            headers["ETag"] = db.version()
            json = [DictMedia.dict(m) for m in play_next_list]

        return {"code": code, "headers": headers, "json": json}

    def clearplaynextlist(self, db, request):
        api.clear_play_next_list(db)
        code = 200

        return {"code": code}

    def scan(self, db, request):
        code, json = 400, None
        api_params = request["api_params"]

        item_id = api_params[-1]

        if item_id and len(api_params) == 2:
            container_id = api.scan(db, item_id)

            if container_id:
                code = 200
                json = DictContainer.dict(
                    api.get_container(db, container_id)
                )
            else:
                code = 404

        return {"code": code, "json": json}

    def identify(self, db, request):
        code, json = 400, None
        api_params = request["api_params"]

        is_container = api_params[1] == "c"
        is_media = api_params[1] == "m"
        item_id = api_params[-1]

        if item_id and len(api_params) == 3 and (is_media or is_container):
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
                code = 200
                json = {'identified': identified}
                if identified:
                    json = {**json, **item_dict}
                else:
                    json = {**json, 'data_id': item_id}
            else:
                code = 404

        return {"code": code, "json": json}

    def play(self, db, request):
        code = 400
        api_params = request["api_params"]

        media_ids = api_params[-1].split(",")

        if len(media_ids) > 0:
            api.play(db, media_ids)
            code = 200

        return {"code": code}

    def played(self, db, request):
        code, json = 400, None
        api_params = request["api_params"]

        is_container = api_params[1] == "c"
        is_media = api_params[1] == "m"
        played = api_params[2] == "1"
        item_id = api_params[-1]

        if item_id and len(api_params) == 4 and (is_media or is_container):
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
                code = 200
                json = {**message, 'data_id': item_id}
            else:
                code = 404

        return {"code": code, "json": json}

    def info(self, db, request):
        code, json = 400, None
        api_params = request["api_params"]

        is_container = api_params[1] == "c"
        is_media = api_params[1] == "m"
        item_id = api_params[-1]

        if item_id and len(api_params) == 3 and (is_media or is_container):
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
                code = 200
                if updated:
                    json = item_dict
            else:
                code = 404

        return {"code": code, "json": json}

    def addmedialibrary(self, db, request):
        code = 400

        media_library_param = self.path.replace("/addmedialibrary/", "")
        if media_library_param:
            from urllib.parse import unquote
            media_library_path = unquote(media_library_param)

            if api.add_media_library(db, media_library_path):
                code = 200
            else:
                code = 404

        return {"code": code}

    def router(self, db, request):
        response = None

        if self.path == "/frontpage":
            response = self.frontpage(db, request)

        elif self.path.startswith("/c/"):
            response = self.container(db, request)

        elif self.path.startswith("/m/"):
            response = self.media(db, request)

        elif self.path.startswith("/playnextlist"):
            response = self.playnextlist(db, request)

        elif self.path.startswith("/clearplaynextlist"):
            response = self.clearplaynextlist(db, request)

        elif self.path.startswith("/scan/"):
            response = self.scan(db, request)

        elif self.path.startswith("/identify/"):
            response = self.identify(db, request)

        elif self.path.startswith("/play/"):
            response = self.play(db, request)

        elif self.path.startswith("/played/"):
            response = self.played(db, request)

        elif self.path.startswith("/info/"):
            response = self.info(db, request)

        elif self.path.startswith("/addmedialibrary/"):
            response = self.addmedialibrary(db, request)

        return super().router(db, request) if response is None else response
