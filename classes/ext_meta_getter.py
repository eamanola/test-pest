import http.client


class Ext_Meta_Getter(object):
    IMAGE_PREFIX = None
    META_ID_PREFIX = None
    POSTER_FOLDER = ["images", "posters"]

    def __init__(self, ext_id):
        super(Ext_Meta_Getter, self).__init__()
        self._api_host = None
        self._api_path = None
        self._image_prefix = None

    def get(self):
        if False:
            import os
            import sys

            f = open(os.path.join(sys.path[0], "data.gz"), "rb")
            data = f.read()

        else:
            conn = http.client.HTTPConnection(self._api_host)
            conn.request("GET", self._api_path)
            response = conn.getresponse()
            data = response.read()
            conn.close()

        return self.parse(data)

    def parse(self, data):
        raise NotImplementedError

    def download_image(self, host, path, filename, rewrite=False):
        import os
        import sys

        poster_folder = os.sep.join(Ext_Meta_Getter.POSTER_FOLDER)
        full_filename = os.path.join(sys.path[0], poster_folder, filename)

        if rewrite or not os.path.exists(full_filename):
            conn = http.client.HTTPConnection(host)
            conn.request("GET", path)
            response = conn.getresponse()
            data = response.read()
            conn.close()

            if not os.path.exists(os.path.join(sys.path[0], poster_folder)):
                os.makedirs(os.path.join(sys.path[0], poster_folder))

            f = open(full_filename, 'wb')
            f.write(data)
            f.close()

    def save(self):
        raise NotImplementedError

    def title(self):
        return self._title

    def description(self):
        return self._description

    def rating(self):
        return self._rating

    def poster(self):
        self._poster
