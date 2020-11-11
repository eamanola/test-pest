import sys
import os
import subprocess
import re

STREAM_FOLDER = os.path.join(sys.path[0], "streams")
VIDEO_FOLDER = os.path.join(STREAM_FOLDER, "video")
SUBTITLES_FOLDER = os.path.join(STREAM_FOLDER, "subtitles")
AUDIO_FOLDER = os.path.join(STREAM_FOLDER, "audio")
TMP_FOLDER = os.path.join(STREAM_FOLDER, "tmp")
R_SUB_AUDIO = r'.*Stream\ #0:([0-9]+)(?:\(([a-zA-Z]{3})\))?.*'


def _create_subtitles(stream_lines, media_id, file_path, format=None):
    count = 0

    re_sub_audio = re.compile(R_SUB_AUDIO)

    for subtitle_line in [s for s in stream_lines if "Subtitle" in s]:
        info = re_sub_audio.search(subtitle_line)
        if info:
            file_name = f'{media_id}.{info.group(2)}'

            if "(default)" in subtitle_line:
                file_name = f'{file_name}.default'

            file_name = f'{file_name}.vtt'

            subtitle_path = os.path.join(
                SUBTITLES_FOLDER,
                file_name
            )

            if not os.path.exists(subtitle_path):
                cmd = (
                    'ffmpeg', '-y', '-hide_banner', '-loglevel', 'warning',
                    '-i', file_path,
                    '-map', f'0:{info.group(1)}',
                    '-f', 'webvtt',
                    subtitle_path
                )

                print("Subtitle:", " ".join(cmd))

                if subprocess.call(cmd) == 0:
                    print('Subtitle: Completed 0')

                    count = count + 1
                else:
                    print('Subtitle: Fail')
                    print('TODO: Bitmap subtitles')

                    os.remove(subtitle_path)
                    print(subtitle_path, "removed")

    return count


def _create_audio_file(file_path, stream_index, audio_path, tmp_path):
    cmd = (
        'ffmpeg', '-y', '-hide_banner', '-loglevel', 'warning',
        '-i', file_path,
        '-map', f'0:{stream_index}',
        '-c:a', 'libopus',
        tmp_path
    )

    print("Audio:", " ".join(cmd))

    if subprocess.call(cmd) == 0:
        print('Audio: Completed 0')

        from shutil import copyfile
        copyfile(tmp_path, audio_path)
    else:
        print('Audio: Fail')

        if os.path.exists(tmp_path):
            os.remove(tmp_path)
            print(tmp_path, "removed")


def _create_audio(stream_lines, media_id, file_path):
    from multiprocessing import Process
    import time

    count = 0

    re_sub_audio = re.compile(R_SUB_AUDIO)

    audio_lines = [line for line in stream_lines if "Audio" in line]

    for line in audio_lines:
        if "(default)" in line:
            audio_lines.remove(line)
            audio_lines.insert(0, line)
            break

    if len(audio_lines) > 0:
        audio_lines.pop(0)

    for line in audio_lines:
        info = re_sub_audio.search(line)
        if info:
            audio_path = os.path.join(
                AUDIO_FOLDER,
                f'{media_id}.{info.group(2)}.opus'
            )

            if not os.path.exists(audio_path):
                tmp_path = os.path.join(
                    TMP_FOLDER,
                    f'audio_{media_id}.{info.group(2)}.opus'
                )
                audio_process = Process(
                    target=_create_audio_file,
                    name=tmp_path,
                    args=(file_path, info.group(1), audio_path, tmp_path))
                audio_process.daemon = True
                audio_process.start()

                time.sleep(1)

                count = count + 1

    return count


def _get_stream_info(file_path):
    cmd = ('ffmpeg', '-hide_banner', '-i', file_path)

    ffmpeg_info = subprocess.run(cmd, capture_output=True, text=True)

    # ffmpeg requires an OUTPUT file use stderr
    return [
        line for line in ffmpeg_info.stderr.split("\n") if "Stream" in line
    ]


def _transcode(file_path, stream_path, tmp_path, codec, width, height):
    cmd = None

    if codec in ("vp8", "vp9"):
        cmd = [
            'ffmpeg',
            '-y', '-hide_banner', '-loglevel', 'warning', '-stats',
            '-i', file_path,
            '-r', '30', '-g', '90',
            '-quality', 'realtime',
            '-qmin', '4', '-qmax', '48',
            '-c:a', 'libopus', '-f', 'webm',
            '-speed', '10',
            '-map', '0:v:0', '-map', '0:a:0',
            '-map', '-0:s', '-map', '-0:d', '-map', '-0:t'
        ]

        if codec == "vp9":
            cmd = cmd + ['-c:v', 'vp9', '-row-mt', '1']
        elif codec == "vp8":
            cmd = cmd + ['-c:v', 'libvpx']

        if width <= 426 and height <= 240:
            cmd = cmd + [
                '-vf',
                'scale=w=426:h=240:force_original_aspect_ratio=decrease',
                # '-speed', '8',
                '-threads', '2', '-b:v', '365k'
            ]
            if codec == "vp9":
                cmd = cmd + [
                    '-tile-columns', '0', '-frame-parallel', '0'
                ]

        elif width <= 640 and height <= 360:
            cmd = cmd + [
                '-vf',
                'scale=w=640:h=360:force_original_aspect_ratio=decrease',
                # '-speed', '7',
                '-threads', '4', '-b:v', '730k'
            ]
            if codec == "vp9":
                cmd = cmd + [
                    '-tile-columns', '1', '-frame-parallel', '0'
                ]

        elif width <= 854 and height <= 480:
            cmd = cmd + [
                '-vf',
                'scale=w=854:h=480:force_original_aspect_ratio=decrease',
                # '-speed', '6',
                '-threads', '4', '-b:v', '1800k'
            ]
            if codec == "vp9":
                cmd = cmd + [
                    '-tile-columns', '1', '-frame-parallel', '1'
                ]

        elif width <= 1280 and height <= 720:
            cmd = cmd + [
                '-vf',
                'scale=w=1280:h=720:force_original_aspect_ratio=decrease',
                # '-speed', '5', -threads 8
                '-threads', '4', '-b:v', '3000k'
            ]
            if codec == "vp9":
                cmd = cmd + [
                    '-tile-columns', '2', '-frame-parallel', '1'
                ]

        elif width <= 1920 and height <= 1080:
            cmd = cmd + [
                '-vf',
                'scale=w=1920:h=1080:force_original_aspect_ratio=decrease',
                # '-speed', '5', -threads 8
                '-threads', '4', '-b:v', '4500k'
            ]
            if codec == "vp9":
                cmd = cmd + [
                    '-tile-columns', '2', '-frame-parallel', '1'
                ]

        elif width <= 2560 and height <= 1440:
            cmd = cmd + [
                '-vf',
                'scale=w=2560:h=1440:force_original_aspect_ratio=decrease',
                # '-speed', '5', -threads 16
                '-threads', '4', '-b:v', '6000k'
            ]
            if codec == "vp9":
                cmd = cmd + [
                    '-tile-columns', '3', '-frame-parallel', '1'
                ]

        elif width <= 3840 and height <= 2160:
            cmd = cmd + [
                '-vf',
                'scale=w=3840:h=2160:force_original_aspect_ratio=decrease',
                # '-speed', '5', -threads 16
                '-threads', '4', '-b:v', '7800k'
            ]
            if codec == "vp9":
                cmd = cmd + [
                    '-tile-columns', '3', '-frame-parallel', '1'
                ]

        cmd = cmd + [
            tmp_path
        ]

    if cmd:
        print('Transcode:', ' '.join(cmd))

        # subprocess.Popen(cmd)
        if subprocess.call(cmd) == 0:
            print("Transcode: Completed 0")

            from shutil import copyfile
            copyfile(tmp_path, stream_path)
        else:
            print('Transcode: Fail / Interrupt')

            if os.path.exists(tmp_path):
                os.remove(tmp_path)
                print(tmp_path, "removed")


def _get_width_height(stream_lines, screen_w, screen_h):
    width, height = screen_w, screen_h

    is_portait = height > width
    if is_portait:
        width, height = height, width

    for line in stream_lines:
        # first
        if "Video" in line:
            video_dimensions = re.compile(r'(\d+)x(\d+)').search(line)
            if video_dimensions:
                if int(video_dimensions.group(1)) < width:
                    width = int(video_dimensions.group(1))

                if int(video_dimensions.group(2)) < height:
                    height = int(video_dimensions.group(2))

            break

    return width, height


def _create_video(stream_lines, media_id, file_path, codec, width, height):
    from multiprocessing import Process
    import time

    file_name = f'{media_id}[{codec}][{width}x{height}].webm'
    w, h = _get_width_height(stream_lines, width, height)
    stream_path = os.path.join(VIDEO_FOLDER, file_name)
    tmp_path = os.path.join(TMP_FOLDER, f'video_{file_name}')

    transcode_process = Process(
        target=_transcode,
        name=tmp_path,
        args=(file_path, stream_path, tmp_path, codec, w, h))
    transcode_process.daemon = True  # why this breaks everything
    transcode_process.start()

    time.sleep(1)

    return os.path.exists(tmp_path)


def _create_stream(media, codec, width, height):
    media_id = media.id()

    file_path = os.path.join(media.parent().path(), media.file_path())
    if not os.path.exists(file_path):
        return None

    stream_lines = _get_stream_info(file_path)

    if not _create_video(
        stream_lines,
        media_id,
        file_path,
        codec,
        width,
        height
    ):
        return None
    _create_audio(stream_lines, media_id, file_path)
    _create_subtitles(stream_lines, media_id, file_path)

    return get_streams(media, codec, width, height)


def format_stream(file_name, is_tmp=False):
    return f'/{ "video" if is_tmp is False else "tmp" }/{file_name}'


def format_audio(file_name, is_tmp=False):
    lang = None

    parts = file_name.split('.')
    if len(parts) == 3:
        lang = parts[1]

    return {
        'src': f'/{ "audio" if is_tmp is False else "tmp" }/{file_name}',
        'lang': lang
    }


def format_subtitle(file_name, is_tmp=False):
    lang = None
    is_default = False

    parts = file_name.split('.')
    if len(parts) == 3:
        lang = parts[1]
    elif len(parts) == 4:
        lang = parts[1]
        is_default = parts[2] == "default"

    return {
        'src': f'/{ "subtitles" if is_tmp is False else "tmp" }/{file_name}',
        'lang': lang,
        'default': is_default
    }


def get_streams(media, codec, width, height):
    streams = []
    audio = []
    subtitles = []

    is_portait = height > width
    if is_portait:
        temp = height
        height = width
        width = temp
    # TODO: brackets? see after mp4

    media_id = media.id()

    for dirpath, dirnames, filenames in os.walk(TMP_FOLDER):
        for file_name in [f for f in filenames if media_id in f]:
            if (
                file_name.startswith("video_")
                and f'[{codec}]' in file_name
                and f'[{width}x{height}]' in file_name
            ):
                streams.append(format_stream(file_name, is_tmp=True))

            elif file_name.startswith("audio_"):
                audio.append(format_audio(file_name, is_tmp=True))

            elif file_name.startswith("subtitle_"):
                subtitles.append(format_subtitle(file_name, is_tmp=True))

    for dirpath, dirnames, filenames in os.walk(VIDEO_FOLDER):
        for file_name in [f for f in filenames if (
            media_id in f
            and f'[{codec}]' in f
            and f'[{width}x{height}]' in f
        )]:
            streams.append(format_stream(file_name))

    if len(streams) == 0:
        return _create_stream(media, codec, width, height)

    for dirpath, dirnames, filenames in os.walk(AUDIO_FOLDER):
        for file_name in [f for f in filenames if f.startswith(media_id)]:
            audio.append(format_audio(file_name))

    for dirpath, dirnames, filenames in os.walk(SUBTITLES_FOLDER):
        for file_name in [f for f in filenames if f.startswith(media_id)]:
            subtitles.append(format_subtitle(file_name))

    return {
        'streams': streams,
        'audio': audio,
        'subtitles': subtitles
    }
