import http.client


class Ext_Meta_Getter(object):
    IMAGE_PREFIX = None
    META_ID_PREFIX = None

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
