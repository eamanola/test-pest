import sys
import os
import subprocess
import re

STREAM_FOLDER = [sys.path[0], "streams"]
VIDEO_FOLDER = os.sep.join([sys.path[0], "streams"] + ["video"])
SUBTITLES_FOLDER = os.sep.join([sys.path[0], "streams"] + ["subtitles"])
AUDIO_FOLDER = os.sep.join([sys.path[0], "streams"] + ["audio"])
R_SUB_AUDIO = r'.*Stream\ #0:([0-9]+)\(([a-zA-Z]{3})\).*'


def _create_subtitles(stream_lines, media_id, file_path, format=None):
    re_sub_audio = re.compile(R_SUB_AUDIO)
    for stream_line in stream_lines:
        if "Subtitle" in stream_line:
            print(stream_line)
            info = re_sub_audio.search(stream_line)
            if info:
                print(f'Subtitle stream {info.group(1)}: {info.group(2)}')
                subtitle_path = os.path.join(
                    SUBTITLES_FOLDER,
                    f'{media_id}.{info.group(2)}'
                )
                cmd = [
                    'ffmpeg',
                    '-y', '-hide_banner',
                    '-i', file_path,
                    '-map', f'0:{info.group(1)}',
                    '-f', 'webvtt',
                    f'{subtitle_path}.vtt'
                ]

                if subprocess.call(cmd) != 0:
                    os.remove(f'{subtitle_path}.vtt')
                    # try bitmap formats


def _create_audio(stream_lines, media_id, file_path):
    # TODO: ?
    re_sub_audio = re.compile(R_SUB_AUDIO)
    for stream_line in stream_lines:
        if "Audio" in stream_line:
            print(stream_line)
            info = re_sub_audio.search(stream_line)
            if info:
                print(f'Audio stream {info.group(1)}: {info.group(2)}')


def _get_stream_info(file_path):
    cmd = ('ffmpeg', '-hide_banner', '-i', file_path)

    ffmpeg_info = subprocess.run(cmd, capture_output=True, text=True)

    # ffmpeg requires an OUTPUT file use stderr
    return [
        line for line in ffmpeg_info.stderr.split("\n") if "Stream" in line
    ]


def _create_default_stream(db, media_id, file_path):
    stream_path = os.path.join(
        VIDEO_FOLDER,
        media_id + os.path.splitext(file_path)[1]
    )
    os.symlink(file_path, stream_path)

    if not os.path.exists(stream_path):
        return None

    stream_lines = _get_stream_info(file_path)

    _create_subtitles(stream_lines, media_id, file_path)
    _create_audio(stream_lines, media_id, file_path)

    return get_streams(db, media_id)


def get_streams(db, media_id):
    TEST = True

    if TEST:
        media_id = "6d6c38560dcd3c17831c1910b1f9525a"

    streams = []
    for dirpath, dirnames, filenames in os.walk(
        VIDEO_FOLDER,
        followlinks=True
    ):
        for filename in filenames:
            if filename.startswith(media_id):
                streams.append(filename)

    if len(streams) == 0:
        media = db.get_media(media_id)
        if not media:
            return None

        file_path = os.path.join(media.parent().path(), media.file_path())
        if not os.path.exists(file_path):
            return None

        return _create_default_stream(db, media_id, file_path)

    subtitles = []
    for dirpath, dirnames, filenames in os.walk(
        SUBTITLES_FOLDER,
        followlinks=True
    ):
        for filename in filenames:
            if filename.startswith(media_id):
                parts = filename.split('.')
                if len(parts) == 3:
                    lang = parts[1]
                    if lang == "eng":
                        lang = "en"
                else:
                    lang = None

                subtitles.append({'src': filename, 'lang': lang})

    audio = []
    for dirpath, dirnames, filenames in os.walk(
        AUDIO_FOLDER,
        followlinks=True
    ):
        for filename in filenames:
            if filename.startswith(media_id):
                audio.append(filename)

    if TEST:
        streams.append('xxx6d6c38560dcd3c17831c1910b1f9525a.webm')

    return {
        'streams': [
            f'/video/{stream}' for stream in streams
        ],
        'subtitles': [
            {
                'src': f'/subtitles/{subtitle["src"]}',
                'lang': subtitle["lang"]

            } for subtitle in subtitles
        ]
    }
