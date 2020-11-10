import sys
import os
import subprocess
import re

STREAM_FOLDER = [sys.path[0], "streams"]
VIDEO_FOLDER = os.sep.join([sys.path[0], "streams"] + ["video"])
SUBTITLES_FOLDER = os.sep.join([sys.path[0], "streams"] + ["subtitles"])
AUDIO_FOLDER = os.sep.join([sys.path[0], "streams"] + ["audio"])
R_SUB_AUDIO = r'.*Stream\ #0:([0-9]+)(?:\(([a-zA-Z]{3})\))?.*'


def _create_subtitles(stream_lines, media_id, file_path, format=None):
    count = 0

    re_sub_audio = re.compile(R_SUB_AUDIO)

    for stream_line in stream_lines:
        if "Subtitle" in stream_line:
            info = re_sub_audio.search(stream_line)
            if info:
                subtitle_path = os.path.join(
                    SUBTITLES_FOLDER,
                    f'{media_id}.{info.group(2)}.vtt'
                )

                if not os.path.exists(subtitle_path):
                    cmd = (
                        'ffmpeg', '-y', '-hide_banner', '-loglevel', 'warning',
                        '-i', file_path,
                        '-map', f'0:{info.group(1)}',
                        '-f', 'webvtt',
                        subtitle_path
                    )

                    try:
                        print("Subtitle:", " ".join(cmd))

                        if subprocess.call(cmd) != 0:
                            print('Subtitle: Fail')
                            print('TODO: Bitmap subtitles')

                            os.remove(subtitle_path)
                            print(subtitle_path, "removed")
                        else:
                            print('Subtitle: Completed 0')

                            count = count + 1

                    # Doesn't fire | TODO:
                    except(SystemExit, KeyboardInterrupt):
                        os.remove(subtitle_path)
                        print(subtitle_path, "removed")
                        raise

    return count


def _create_audio(stream_lines, media_id, file_path):
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
        if "Audio" in line:
            info = re_sub_audio.search(line)
            if info:
                audio_path = os.path.join(
                    AUDIO_FOLDER,
                    f'{media_id}.{info.group(2)}.opus'
                ).strip(".")

                if not os.path.exists(audio_path):
                    cmd = (
                        'ffmpeg', '-y', '-hide_banner', '-loglevel', 'warning',
                        '-i', file_path,
                        '-map', f'0:{info.group(1)}',
                        '-c:a', 'libopus',
                        audio_path
                    )

                    try:
                        print("Audio:", " ".join(cmd))

                        if subprocess.call(cmd) != 0:
                            print('Audio: Fail')

                            os.remove(audio_path)
                            print(audio_path, "removed")
                        else:
                            print('Audio: Completed 0')

                            count = count + 1

                    # Doesn't fire | TODO:
                    except(SystemExit, KeyboardInterrupt):
                        os.remove(audio_path)
                        print(audio_path, "removed")
                        raise

    return count


def _get_stream_info(file_path):
    cmd = ('ffmpeg', '-hide_banner', '-i', file_path)

    ffmpeg_info = subprocess.run(cmd, capture_output=True, text=True)

    # ffmpeg requires an OUTPUT file use stderr
    return [
        line for line in ffmpeg_info.stderr.split("\n") if "Stream" in line
    ]


def _transcode(file_path, stream_path):
    cmd = (
        'ffmpeg',
        '-y', '-hide_banner', '-loglevel', 'warning', '-stats',
        '-i', file_path,
        '-r', '30',
        '-g', '90',
        '-vf', 'scale=w=1920:h=1080:force_original_aspect_ratio=decrease',
        '-quality', 'realtime',
        '-speed', '10',
        '-threads', '4',
        '-row-mt', '1',
        '-tile-columns', '2',
        '-frame-parallel', '1',
        '-qmin', '4', '-qmax', '48',
        '-b:v', '4500k',
        '-map', '0:v:0', '-map', '0:a:0',
        '-map', '-0:s', '-map', '-0:d', '-map', '-0:t',
        stream_path
    )

    try:
        print('Transcode:', ' '.join(cmd))

        if subprocess.call(cmd) != 0:
            print('Transcode: Fail / Interrupt')

            os.remove(stream_path)
            print(stream_path, "removed")
            # subprocess.Popen(cmd)
        else:
            print("Transcode: Completed 0")

    # Doesn't fire | TODO:
    except (SystemExit, KeyboardInterrupt):
        os.remove(stream_path)
        print(stream_path, "removed")
        raise


def _create_stream(media_id, file_path):
    stream_path = os.path.join(VIDEO_FOLDER, f'{media_id}.webm')

    import threading
    transcode_thread = threading.Thread(
        target=_transcode,
        name="TrancodeThread",
        args=(file_path, stream_path))
    # transcode_thread.daemon = True  # why this breaks everything
    transcode_thread.start()

    import time
    time.sleep(1)

    if not os.path.exists(stream_path):
        return None

    stream_lines = _get_stream_info(file_path)

    subtitles_created = _create_subtitles(stream_lines, media_id, file_path)
    audio_created = _create_audio(stream_lines, media_id, file_path)

    buffer_time = 10 - (0.5 * subtitles_created) - (15 * audio_created)
    if buffer_time > 0:
        time.sleep(int(buffer_time))

    return get_streams(None, media_id)


def get_streams(db, media_id):
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

        # file_path = os.path.join(sys.path[0], "test", "sample-video-12s.mkv")
        return _create_stream(media_id, file_path)

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
                parts = filename.split('.')
                if len(parts) == 3:
                    lang = parts[1]
                else:
                    lang = None

                audio.append({'src': filename, 'lang': lang})

    return {
        'streams': [
            f'/video/{stream}' for stream in streams
        ],
        'subtitles': [
            {
                'src': f'/subtitles/{subtitle["src"]}',
                'lang': subtitle["lang"]

            } for subtitle in subtitles
        ],
        'audio': [
            {
                'src': f'/audio/{a["src"]}',
                'lang': a["lang"]

            } for a in audio
        ]
    }
