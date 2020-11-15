import sys
import os
import subprocess
import re
import time
import tempfile

STREAM_FOLDER = os.path.join(sys.path[0], "streams")
FONTS_FOLDER = os.path.join(STREAM_FOLDER, "fonts")
PROCESS_NAME_PREFIX = "test-pest"
R_SUB_AUDIO = r'.*Stream\ #0:([0-9]+)(?:\(([a-zA-Z]{3})\))?.*'
R_DURATION = r'.*Duration\:\ (\d\d)\:(\d\d)\:(\d\d).*'


class Static_vars(object):
    current_video_proc = None


def _get_stream_info(file_path):
    cmd = ('ffmpeg', '-hide_banner', '-i', file_path)

    ffmpeg_info = subprocess.run(cmd, capture_output=True, text=True)

    # ffmpeg requires an OUTPUT file use stderr
    return ffmpeg_info.stderr.split("\n")


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


def _video_stream(file_path, codec, width, height, media_id, start_time):
    cmd = None

    if codec in ("vp8", "vp9"):
        cmd = [
            'ffmpeg', '-y', '-hide_banner',
            '-loglevel', 'warning', '-stats',
            '-ss', start_time,
            '-i', file_path,
            '-r', '30', '-g', '90',
            '-quality', 'realtime',
            '-qmin', '4', '-qmax', '48',
            '-c:a', 'libopus', '-f', 'webm',
            '-speed', '10',
            '-map', '0:v:0', '-map', '0:a:0',
            '-sn', '-dn', '-map', '-0:t'
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

    # https://stackoverflow.com/questions/10114224/how-to-properly-send-http-response-with-python-using-socket-library-only
    if False:
        output = [
            '-content_type', 'video/webm',
            '-listen', '1',
            '-headers',
            'Cache-Control: private, must-revalidate, max-age=0\r\n\r\n',
            f'http://192.168.1.119:8099/{media_id}.webm'
        ]
    elif True:
        output = [os.path.join(tempfile.gettempdir(), f'ab.webm')]

    if cmd:
        cmd = cmd + output
        print('Transcode:', ' '.join(cmd))

        if Static_vars.current_video_proc is not None:
            if Static_vars.current_video_proc.poll() is None:
                print("Closing previous video transcoding")
                Static_vars.current_video_proc.terminate()

        ffmpeg_proc = subprocess.Popen(
            cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE
        )
        Static_vars.current_video_proc = ffmpeg_proc

        time.sleep(1)

        if ffmpeg_proc.poll() is not None and ffmpeg_proc.returncode == 1:
            print('Transcode fail')

            stderr_str = ffmpeg_proc.stderr.read().decode("utf-8")

            # http://trac.ffmpeg.org/ticket/5718
            if any(
                (
                    "libopus" in line
                    and "Invalid channel layout 5.1(side)" in line
                ) for line in stderr_str.split("\n")
            ):
                print('Trying to map channels manually')
                for i in range(len(cmd)):
                    if cmd[i] == 'libopus':
                        cmd.insert(i + 1, "-af")
                        cmd.insert(i + 2, 'aformat=channel_layouts=5.1|stereo')
                        break

                print('(Re:) Transcode:', ' '.join(cmd))

                ffmpeg_proc = subprocess.Popen(
                    cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE
                )
                Static_vars.current_video_proc = ffmpeg_proc
                time.sleep(1)

        return output[0]


def _audio_stream(file_path, stream_index, dst_path):
    cmd = (
        'ffmpeg', '-y', '-hide_banner', '-loglevel', 'warning',
        '-i', file_path,
        '-map', f'0:{stream_index}',
        '-c:a', 'libopus',
        dst_path
    )

    print("Audio:", " ".join(cmd))

    subprocess.Popen(cmd)
    time.sleep(1)

    return dst_path


def _subtitle(file_path, stream_index, dst_path):
    cmd = (
        'ffmpeg', '-y', '-hide_banner', '-loglevel', 'warning',
        '-i', file_path,
        '-map', f'0:{stream_index}',
        dst_path
    )

    print("Subtitle:", " ".join(cmd))

    subprocess.Popen(cmd)
    time.sleep(1)

    return dst_path


def _dump_attachments(file_path, dst_dir):
    cmd = (
        'ffmpeg', '-n', '-hide_banner', '-loglevel', 'warning',
        '-dump_attachment:t', '', '-i', file_path
    )

    print("Fonts:", " ".join(cmd))

    subprocess.Popen(cmd, cwd=dst_dir)
    time.sleep(1)


def get_video_stream(media, codec, width, height, start_time):
    file_path = os.path.join(media.parent().path(), media.file_path())
    if not os.path.exists(file_path):
        return None

    stream_lines = [line for line in _get_stream_info(file_path) if (
        "Stream" in line and "Video" in line
    )]
    w, h = _get_width_height(stream_lines, width, height)

    return _video_stream(file_path, codec, w, h, media.id(), start_time)


def get_audio_stream(media, stream_index):
    file_path = os.path.join(media.parent().path(), media.file_path())
    if not os.path.exists(file_path):
        return None

    from pathlib import Path
    dst_path = os.path.join(
        tempfile.gettempdir(),
        media.id(),
        "audio",
        f'{stream_index}.opus'
    )
    Path(dst_path).parent.mkdir(parents=True, exist_ok=True)

    return _audio_stream(file_path, stream_index, dst_path)


def get_subtitle(media, stream_index):
    file_path = os.path.join(media.parent().path(), media.file_path())
    if not os.path.exists(file_path):
        return None

    is_ass = False
    stream_lines = _get_stream_info(file_path)
    re_sub_audio = re.compile(R_SUB_AUDIO)

    for line in [line for line in stream_lines if "Subtitle" in line]:
        info = re_sub_audio.search(line)
        if info and info.group(1) == stream_index:
            is_ass = "Subtitle: ass" in line
            break

    from pathlib import Path
    dst_path = os.path.join(
        tempfile.gettempdir(),
        media.id(),
        "subtitle",
        f'{stream_index}.{"ass" if is_ass else "vtt"}'
    )
    Path(dst_path).parent.mkdir(parents=True, exist_ok=True)

    return _subtitle(file_path, stream_index, dst_path)


def get_font(media, font_name):
    dst_dir = os.path.join(
        tempfile.gettempdir(),
        media.id(),
        "fonts"
    )

    if not os.path.exists(os.path.join(dst_dir, font_name)):
        if os.path.exists(os.path.join(
            dst_dir, font_name.replace("%20", " ")
        )):
            font_name = font_name.replace("%20", " ")

    dst_path = os.path.join(dst_dir, font_name)

    if not os.path.exists(dst_path):
        file_path = os.path.join(media.parent().path(), media.file_path())
        if not os.path.exists(file_path):
            return None

        from pathlib import Path
        Path(dst_path).parent.mkdir(parents=True, exist_ok=True)

        _dump_attachments(file_path, os.path.dirname(dst_path))

    if not os.path.exists(os.path.join(dst_dir, font_name)):
        if os.path.exists(os.path.join(
            dst_dir, font_name.replace("%20", " ")
        )):
            font_name = font_name.replace("%20", " ")

    return os.path.join(dst_dir, font_name)


def get_streams(media, codec, width, height, start_time):
    file_path = os.path.join(media.parent().path(), media.file_path())
    if not os.path.exists(file_path):
        return None

    media_id = media.id()

    streams = [f'/video/{codec}/{width}/{height}/{media_id}']
    audio = []
    subtitles = []
    fonts = []

    stream_lines = _get_stream_info(file_path)
    re_sub_audio = re.compile(R_SUB_AUDIO)

    for line in [line for line in stream_lines if "Audio" in line]:
        is_default = "(default)" in line
        is_forced = "(forced)" in line

        info = re_sub_audio.search(line)
        stream_index = info.group(1) if info else None
        lang = info.group(2) if info else None

        _audio = {
            'src': f"/audio/{stream_index}/{media_id}",
            'lang': lang,
            'is_forced': is_forced
        }

        if is_default:
            audio.insert(0, _audio)
        else:
            audio.append(_audio)

    if len(audio):
        audio.pop(0)

    for line in [line for line in stream_lines if "Subtitle" in line]:
        is_default = "(default)" in line
        is_forced = "(forced)" in line
        is_ass = "Subtitle: ass" in line

        info = re_sub_audio.search(line)
        stream_index = info.group(1) if info else None
        lang = info.group(2) if info else None
        src = f'/subtitle/{stream_index}/{media_id}'
        src = src + (".ass" if is_ass else ".vtt")

        subtitle = {
            'src': src,
            'lang': lang,
            'default': is_default,
            'forced': is_forced
        }

        if lang is not None:
            subtitles.append(subtitle)

    duration = 0
    for line in stream_lines:
        if "Duration" in line:
            d = re.compile(R_DURATION).search(line)
            if d:
                duration = (
                    int(d.group(1)) * 3600
                    + int(d.group(2)) * 60
                    + int(d.group(3))
                )
            break

    re_attachment_names = re.compile(r"^\s*filename\s*\:\s*(.*)\s*$")
    for line in [
        line for line in stream_lines if (
            line.strip().startswith("filename")
            and line.strip().endswith((".otf", ".OTF", ".ttf", ".TTF"))
        )
    ]:
        filename = re_attachment_names.search(line)
        if filename:
            f = filename.group(1)
            if os.path.exists(os.path.join(FONTS_FOLDER, f)):
                fonts.append(f"/fonts/{media_id}/{f}")

    return {
        'id': media_id,
        'streams': streams,
        'audio': audio,
        'subtitles': subtitles,
        'duration': duration,
        'fonts': fonts
    }
