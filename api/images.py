import sys
import os


class Images(object):
    THUMBNAIL_FOLDER = ['images', 'thumbnails']
    POSTER_FOLDER = ['images', 'posters']

    def __init__(self):
        super(Images, self).__init__()

    def thumbnail(media, create_ifmissing=False):
        import subprocess
        ret = None

        if (
            create_ifmissing and
            media and
            media.thumbnail() and
            media.file_path() and
            media.parent()
        ):

            thumbnail_path = os.path.join(
                sys.path[0],
                os.sep.join(Images.THUMBNAIL_FOLDER),
                f"{media.thumbnail()}.png"
            )

            if not os.path.exists(thumbnail_path):
                if not os.path.exists(os.path.dirname(thumbnail_path)):
                    os.makedirs(os.path.dirname(thumbnail_path))

                input = os.path.join(
                    media.parent().path(),
                    media.file_path()
                )

                cmd = [
                    'ffmpeg',
                    '-ss', '00:04:00.000',
                    '-i', input,
                    '-vf', 'scale=240:-1',
                    '-y',
                    '-vframes', '1',
                    thumbnail_path
                ]

                if "unittest" in sys.argv[0]:
                    stdout = stderr = subprocess.DEVNULL
                else:
                    stdout = stderr = None

                subprocess.run(
                    cmd,
                    stdout=stdout,
                    stderr=stderr
                )

                # video shorter than 4 min
                if not os.path.exists(thumbnail_path):
                    cmd[2] = "00:00:10.000"
                    subprocess.run(
                        cmd,
                        stdout=stdout,
                        stderr=stderr
                    )

        return f'{"/".join(Images.THUMBNAIL_FOLDER)}/{media.thumbnail()}.png'

    def poster(identifiable):
        poster = None

        if (
            identifiable and
            identifiable.meta() and
            identifiable.meta().image_name()
        ):
            poster = (
                f'''{
                    "/".join(Images.POSTER_FOLDER)
                }/{
                    identifiable.meta().image_name()
                }'''
            )

        return poster

    def download_poster(url, poster_filename, rewrite=False):
        full_dest_filename = os.path.join(
            sys.path[0],
            os.sep.join(Images.POSTER_FOLDER),
            poster_filename
        )

        return Images.download(url, full_dest_filename, rewrite=rewrite)

    def download(url, dest_full_path, rewrite=False):
        if rewrite or not os.path.exists(dest_full_path):
            import http.client
            from urllib.parse import urlparse
            parsed_url = urlparse(url)

            try:
                if parsed_url.scheme == "https":
                    conn = http.client.HTTPSConnection(parsed_url.netloc)
                else:
                    conn = http.client.HTTPConnection(parsed_url.netloc)
                conn.request("GET", parsed_url.path)
                data = conn.getresponse().read()
            finally:
                conn.close()

            if len(data):
                if not os.path.exists(os.path.dirname(dest_full_path)):
                    os.makedirs(os.path.dirname(dest_full_path))

                with open(dest_full_path, 'wb') as f:
                    f.write(data)
