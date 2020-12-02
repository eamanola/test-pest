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

    def download_poster(
        host, path, poster_filename, rewrite=False, https=False
    ):
        full_dest_filename = os.path.join(
            sys.path[0],
            os.sep.join(Images.POSTER_FOLDER),
            poster_filename
        )

        return Images.download(
            host, path, full_dest_filename, rewrite=rewrite, https=https
        )

    def download(host, path, dest_full_path, rewrite=False, https=False):
        import http.client
        if rewrite or not os.path.exists(dest_full_path):
            if https:
                conn = http.client.HTTPSConnection(host)
            else:
                conn = http.client.HTTPConnection(host)
            conn.request("GET", path)
            response = conn.getresponse()
            data = response.read()
            conn.close()

            if not os.path.exists(os.path.dirname(dest_full_path)):
                os.makedirs(os.path.dirname(dest_full_path))

            f = open(dest_full_path, 'wb')
            f.write(data)
            f.close()

        return 0
