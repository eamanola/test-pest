import os
import sys
import time
import gzip


class MetaCache(object):
    META_FOLDER = os.path.join(sys.path[0], "meta")

    def load(key, max_age=7*24*60*60):
        meta = None

        file_path = os.path.join(MetaCache.META_FOLDER, f'{key}.gz')

        if (
            os.path.exists(file_path)
            and time.time() - int(os.path.getmtime(file_path)) < max_age
        ):
            print('meta from file')

            with gzip.open(file_path, "rb") as f:
                meta = f.read()

        return meta

    def save(key, data_bytes):
        import gzip

        file_path = os.path.join(MetaCache.META_FOLDER, f'{key}.gz')
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with gzip.open(file_path, "wb") as f:
            meta = f.write(data_bytes)

        return 0
