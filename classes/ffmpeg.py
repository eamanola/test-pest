from CONFIG import (
    CFFMPEG_STREAM, CFFMPEG_HOST, CFFMPEG_PORT, CFFMPEG_LEGLEVEL, CTMP_DIR
)


class FFMpeg(object):
    """docstring for FFMpeg."""

    def __init__(self):
        super(FFMpeg, self).__init__()
        self.cmd = []
        self.cmd.append('ffmpeg')

    def log(self, hide_banner=True, stats=False, loglevel=CFFMPEG_LEGLEVEL):
        if hide_banner:
            self.cmd.append('-hide_banner')
        if stats:
            self.cmd.append('-stats')
        if loglevel:
            self.cmd = self.cmd + ['-loglevel', CFFMPEG_LEGLEVEL]

        return self

    def y(self):
        self.cmd.append("-y")
        return self

    def n(self):
        self.cmd.append("-n")
        return self

    def input(self, file_path, ss=None, re=False):
        if ss:
            self.cmd = self.cmd + ["-ss", str(ss)]
        if re:
            self.cmd.append("-re")

        self.cmd = self.cmd + ['-i', file_path]

        return self

    def map(self, stream_identifier):
        if stream_identifier:
            self.cmd = self.cmd + ['-map', stream_identifier]

        return self

    def vcodec(self, codec):
        if codec:
            self.cmd = self.cmd + ['-c:v', codec]

        return self

    def acodec(self, codec):
        if codec:
            self.cmd = self.cmd + ['-c:a', codec]

        return self

    def scodec(self, codec):
        if codec:
            self.cmd = self.cmd + ['-c:s', codec]

        return self

    def format(self, format):
        if format:
            self.cmd = self.cmd + ['-f', format]

        return self

    def copyts(self):
        self.cmd.append('-copyts')
        return self

    def dump_attachment(self):
        self.cmd = self.cmd + ['-dump_attachment:t', '']
        return self

    def filter_complex(self, filter):
        self.cmd = self.cmd + ['-filter_complex', filter]
        return self

    def output(self, output):
        if output:
            self.cmd.append(output)

        return self

    def webm(self, codec="vp9", width=1920, height=1080, max_threads=0):
        self.format('webm')
        self.cmd = self.cmd + [
            '-r', '30', '-g', '90', '-quality', 'realtime',
            '-qmin', '4', '-qmax', '48', '-speed', '10'
        ]

        if codec == "vp9":
            self.vcodec('vp9')
            self.cmd = self.cmd + ['-row-mt', '1']
        elif codec == "vp8":
            self.vcodec('libvpx')

        if width <= 426 and height <= 240:
            self.cmd = self.cmd + [
                '-vf',
                'scale=w=426:h=240:force_original_aspect_ratio=decrease',
                # '-speed', '8',
                '-threads', str(2 if 2 <= max_threads else max_threads),
                '-b:v', '365k', '-bufsize', '730k'
            ]
            if codec == "vp9":
                self.cmd = self.cmd + [
                    '-tile-columns', '0', '-frame-parallel', '0'
                ]

        elif width <= 640 and height <= 360:
            self.cmd = self.cmd + [
                '-vf',
                'scale=w=640:h=360:force_original_aspect_ratio=decrease',
                # '-speed', '7',
                '-threads', str(4 if 4 <= max_threads else max_threads),
                '-b:v', '730k', '-bufsize', '1460k'
            ]
            if codec == "vp9":
                self.cmd = self.cmd + [
                    '-tile-columns', '1', '-frame-parallel', '0'
                ]

        elif width <= 854 and height <= 480:
            self.cmd = self.cmd + [
                '-vf',
                'scale=w=854:h=480:force_original_aspect_ratio=decrease',
                # '-speed', '6',
                '-threads', str(4 if 4 <= max_threads else max_threads),
                '-b:v', '1800k', '-bufsize', '3600k'
            ]
            if codec == "vp9":
                self.cmd = self.cmd + [
                    '-tile-columns', '1', '-frame-parallel', '1'
                ]

        elif width <= 1280 and height <= 720:
            self.cmd = self.cmd + [
                '-vf',
                'scale=w=1280:h=720:force_original_aspect_ratio=decrease',
                # '-speed', '5',
                '-threads', str(8 if 8 <= max_threads else max_threads),
                '-b:v', '3000k', '-bufsize', '6000k'
            ]
            if codec == "vp9":
                self.cmd = self.cmd + [
                    '-tile-columns', '2', '-frame-parallel', '1'
                ]

        elif width <= 1920 and height <= 1080:
            self.cmd = self.cmd + [
                '-vf',
                'scale=w=1920:h=1080:force_original_aspect_ratio=decrease',
                # '-speed', '5',
                '-threads', str(8 if 8 <= max_threads else max_threads),
                '-b:v', '4500k', '-bufsize', '9000k'
            ]
            if codec == "vp9":
                self.cmd = self.cmd + [
                    '-tile-columns', '2', '-frame-parallel', '1'
                ]

        elif width <= 2560 and height <= 1440:
            self.cmd = self.cmd + [
                '-vf',
                'scale=w=2560:h=1440:force_original_aspect_ratio=decrease',
                # '-speed', '5',
                '-threads', str(16 if 16 <= max_threads else max_threads),
                '-b:v', '6000k', '-bufsize', '12000k'
            ]
            if codec == "vp9":
                self.cmd = self.cmd + [
                    '-tile-columns', '3', '-frame-parallel', '1'
                ]

        elif width <= 3840 and height <= 2160:
            self.cmd = self.cmd + [
                '-vf',
                'scale=w=3840:h=2160:force_original_aspect_ratio=decrease',
                # '-speed', '5',
                '-threads', str(16 if 16 <= max_threads else max_threads),
                '-b:v', '7800k', '-bufsize', '15600k'
            ]
            if codec == "vp9":
                self.cmd = self.cmd + [
                    '-tile-columns', '3', '-frame-parallel', '1'
                ]

        return self
