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

    for stream_line in stream_lines:
        if "Subtitle" in stream_line:

            info = re_sub_audio.search(stream_line)
            if info:
                file_name = f'{media_id}.{info.group(2)}'

                if "(default)" in stream_line:
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
    import threading
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
                audio_thread = threading.Thread(
                    target=_create_audio_file,
                    name=f"AudioThread{info.group(2)}",
                    args=(file_path, info.group(1), audio_path, tmp_path))

                audio_thread.start()

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


def _transcode(file_path, stream_path, tmp_path):
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
        tmp_path
    )

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



def _create_stream(media_id, file_path):
    import threading
    import time

    stream_path = os.path.join(VIDEO_FOLDER, f'{media_id}.webm')
    tmp_path = os.path.join(TMP_FOLDER, f'video_{media_id}.webm')

    transcode_thread = threading.Thread(
        target=_transcode,
        name="TrancodeThread",
        args=(file_path, stream_path, tmp_path))
    transcode_thread.daemon = True  # why this breaks everything
    transcode_thread.start()

    time.sleep(1)

    if not os.path.exists(tmp_path):
        return None

    stream_lines = _get_stream_info(file_path)

    _create_audio(stream_lines, media_id, file_path)
    _create_subtitles(stream_lines, media_id, file_path)

    return get_streams(None, media_id)


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


def get_streams(db, media_id):
    streams = []
    audio = []
    subtitles = []

    for dirpath, dirnames, filenames in os.walk(TMP_FOLDER):
        for file_name in [f for f in filenames if media_id in f]:
            if (file_name.startswith("video_")):
                streams.append(format_stream(file_name, is_tmp=True))

            elif (file_name.startswith("audio_")):
                audio.append(format_audio(file_name, is_tmp=True))

            elif (file_name.startswith("subtitle_")):
                subtitles.append(format_subtitle(file_name, is_tmp=True))

    for dirpath, dirnames, filenames in os.walk(
        VIDEO_FOLDER,
        followlinks=True
    ):
        for file_name in [f for f in filenames if f.startswith(media_id)]:
            streams.append(format_stream(file_name))

    if len(streams) == 0:
        media = db.get_media(media_id)
        if not media:
            return None

        file_path = os.path.join(media.parent().path(), media.file_path())
        if not os.path.exists(file_path):
            return None

        # file_path = os.path.join(sys.path[0], "test", "sample-video-12s.mkv")
        return _create_stream(media_id, file_path)

    for dirpath, dirnames, filenames in os.walk(
        AUDIO_FOLDER,
        followlinks=True
    ):
        for file_name in [f for f in filenames if f.startswith(media_id)]:
            audio.append(format_audio(file_name))

    for dirpath, dirnames, filenames in os.walk(
        SUBTITLES_FOLDER,
        followlinks=True
    ):
        for file_name in [f for f in filenames if f.startswith(media_id)]:
            subtitles.append(format_subtitle(file_name))

    return {
        'streams': streams,
        'audio': audio,
        'subtitles': subtitles
    }
