class Identifiable(object):

    def __init__(self):
        super(Identifiable, self).__init__()
        self._year = None
        self._ext_ids = {}
        self._meta = None

    def set_year(self, year):
        self._year = year

    def year(self):
        return self._year

    def ext_ids(self):
        return self._ext_ids

    def set_meta(self, meta):
        self._meta = meta

    def meta(self):
        return self._meta
