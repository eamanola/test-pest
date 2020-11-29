import sys
import os
import subprocess
import re
import time
from CONFIG import (
    CFFMPEG_STREAM, CFFMPEG_HOST, CFFMPEG_PORT, CFFMPEG_LEGLEVEL, CTMP_DIR
)

R_SUB_AUDIO = r'.*Stream\ #0:([0-9]+)(?:\(([a-zA-Z]{3})\))?.*'
R_DURATION = r'.*Duration\:\ (\d\d)\:(\d\d)\:(\d\d).*'

ALWAYS_TRANSCODE = False
ALWAYS_TRANSCODE_AUDIO = ALWAYS_TRANSCODE
ALWAYS_TRANSCODE_VIDEO = ALWAYS_TRANSCODE


def _get_stream_info(file_path):
    cmd = ('ffmpeg', '-hide_banner', '-i', file_path)

    ffmpeg_info = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )
    ffmpeg_info.wait()

    # ffmpeg requires an OUTPUT file use stderr
    return ffmpeg_info.stdout.read().decode("utf8").split("\n")


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


def _video_stream(file_path, codec, width, height, start_time, subtitle_index):
    cmd, mime = None, None

    try:
        max_threads = int(len(os.sched_getaffinity(0)) / 2)
    except Exception:
        max_threads = int(os.cpu_count() / 2)

    max_threads = max_threads if max_threads > 0 else 1

    if codec is None:
        print("Return copy")

    if codec in ("vp8", "vp9"):
        mime = ".webm"
        cmd = [
            'ffmpeg', '-y', '-hide_banner',
            '-loglevel', CFFMPEG_LEGLEVEL  # , '-stats'
        ]

        if not CFFMPEG_STREAM:
            cmd = cmd + ['-re']

        cmd = cmd + [
            '-ss', str(start_time),
            '-i', file_path,
            '-r', '30', '-g', '90',
            '-quality', 'realtime',
            '-qmin', '4', '-qmax', '48',
            '-f', 'webm',
            '-speed', '10',
            '-an', '-sn', '-dn', '-map', '-0:t?'
        ]

        if not CFFMPEG_STREAM:
            cmd = cmd + ['-bufsize', '1M']

        if codec == "vp9":
            cmd = cmd + ['-c:v', 'vp9', '-row-mt', '1']
        elif codec == "vp8":
            cmd = cmd + ['-c:v', 'libvpx']

        if subtitle_index is None:
            cmd = cmd + ['-map', '0:v:0']
        else:
            cmd = cmd + [
                '-filter_complex',
                f'[0:v:0][0:{subtitle_index}]overlay[v]', '-map', '[v]'
            ]

        if width <= 426 and height <= 240:
            cmd = cmd + [
                '-vf',
                'scale=w=426:h=240:force_original_aspect_ratio=decrease',
                # '-speed', '8',
                '-threads', str(2 if 2 <= max_threads else max_threads),
                '-b:v', '365k'
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
                '-threads', str(4 if 4 <= max_threads else max_threads),
                '-b:v', '730k'
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
                '-threads', str(4 if 4 <= max_threads else max_threads),
                '-b:v', '1800k'
            ]
            if codec == "vp9":
                cmd = cmd + [
                    '-tile-columns', '1', '-frame-parallel', '1'
                ]

        elif width <= 1280 and height <= 720:
            cmd = cmd + [
                '-vf',
                'scale=w=1280:h=720:force_original_aspect_ratio=decrease',
                # '-speed', '5',
                '-threads', str(8 if 8 <= max_threads else max_threads),
                '-b:v', '3000k'
            ]
            if codec == "vp9":
                cmd = cmd + [
                    '-tile-columns', '2', '-frame-parallel', '1'
                ]

        elif width <= 1920 and height <= 1080:
            cmd = cmd + [
                '-vf',
                'scale=w=1920:h=1080:force_original_aspect_ratio=decrease',
                # '-speed', '5',
                '-threads', str(8 if 8 <= max_threads else max_threads),
                '-b:v', '4500k'
            ]
            if codec == "vp9":
                cmd = cmd + [
                    '-tile-columns', '2', '-frame-parallel', '1'
                ]

        elif width <= 2560 and height <= 1440:
            cmd = cmd + [
                '-vf',
                'scale=w=2560:h=1440:force_original_aspect_ratio=decrease',
                # '-speed', '5',
                '-threads', str(16 if 16 <= max_threads else max_threads),
                '-b:v', '6000k'
            ]
            if codec == "vp9":
                cmd = cmd + [
                    '-tile-columns', '3', '-frame-parallel', '1'
                ]

        elif width <= 3840 and height <= 2160:
            cmd = cmd + [
                '-vf',
                'scale=w=3840:h=2160:force_original_aspect_ratio=decrease',
                # '-speed', '5',
                '-threads', str(16 if 16 <= max_threads else max_threads),
                '-b:v', '7800k'
            ]
            if codec == "vp9":
                cmd = cmd + [
                    '-tile-columns', '3', '-frame-parallel', '1'
                ]

        cmd.append('pipe:1')

        if subtitle_index is not None:
            cmd = [c for c in cmd if c != "-vf" and not c.startswith("scale")]

    if cmd:
        cmd_test = subprocess.Popen(
            cmd,
            stderr=subprocess.PIPE,
            stdout=subprocess.DEVNULL
        )
        time.sleep(0.5)

        if cmd_test.poll() is not None and cmd_test.returncode == 1:
            print('Video test fail')

            stderr_str = cmd_test.stderr.read().decode("utf-8")

            # fix cmd
            print(stderr_str)
        else:
            cmd_test.terminate()

        if CFFMPEG_STREAM:
            cmd = cmd[:-1] + [
                '-content_type', 'video/webm',
                '-listen', '1',
                '-headers',
                'Cache-Control: private, must-revalidate, max-age=0',
                '-reconnect_streamed', '1',
                f'http://{CFFMPEG_HOST}:{CFFMPEG_PORT}/video.webm'
            ]

        print('Video:', ' '.join(cmd))

        return cmd, mime


def _video_dump(file_path, start_time, dst_path):
    cmd = (
        'ffmpeg', '-y', '-hide_banner', '-loglevel', CFFMPEG_LEGLEVEL,
        '-ss', str(start_time), '-i', file_path,
        '-an', '-sn', '-dn', '-map', '-0:t?', '-map', '0:v:0',
        '-c', 'copy', dst_path
    )

    print('Dump video:')  # , ' '.join(cmd))
    proc = subprocess.Popen(cmd)
    proc.wait()
    # print('Dump video:Done')

    return proc.returncode


def _audio_stream(file_path, stream_index, start_time, format, audio_codec):
    cmd = [
        'ffmpeg', '-y', '-hide_banner', '-loglevel', CFFMPEG_LEGLEVEL,
        '-i', file_path, '-ss', str(start_time),
        '-map', f'0:{stream_index}',
        '-c:a', audio_codec, '-f', format, 'pipe:1'
    ]

    cmd_test = subprocess.Popen(
        cmd,
        stderr=subprocess.PIPE,
        stdout=subprocess.DEVNULL
    )
    time.sleep(0.5)

    if cmd_test.poll() is not None and cmd_test.returncode == 1:
        print('Audio test fail')

        stderr_str = cmd_test.stderr.read().decode("utf-8")

        # http://trac.ffmpeg.org/ticket/5718
        if any((
            "libopus" in line
            and "Invalid channel layout 5.1(side)" in line
        ) for line in stderr_str.split("\n")):
            print('Mapping channels manually')

            cmd.insert(-1, "-af")
            cmd.insert(-1, 'aformat=channel_layouts=5.1|stereo')

        else:
            print(stderr_str)
    else:
        cmd_test.terminate()

    print('Audio:', ' '.join(cmd))

    return cmd


def _audio_dump(file_path, stream_index, start_time, format, dst_path):
    cmd = (
        'ffmpeg', '-y', '-hide_banner', '-loglevel', CFFMPEG_LEGLEVEL,
        '-ss', str(start_time), '-i', file_path,
        '-vn', '-sn', '-dn', '-map', '-0:t?', '-map', f'0:{stream_index}',
        '-c', 'copy', '-f', format, dst_path
    )

    print('Dump audio:', ' '.join(cmd))
    proc = subprocess.Popen(cmd)
    proc.wait()
    # print('Dump audio: Done')

    return proc.returncode


def _subtitle(file_path, stream_index, format):
    cmd = [
        'ffmpeg', '-y', '-hide_banner', '-loglevel', CFFMPEG_LEGLEVEL,
        '-i', file_path, '-f', format
    ]

    if stream_index is not None:
        cmd = cmd + ['-map', f'0:{stream_index}']

    cmd.append('pipe:1')

    print('Subtitle:', ' '.join(cmd))

    return cmd


def _dump_attachments(file_path, dst_dir):
    cmd = (
        'ffmpeg', '-n', '-hide_banner', '-loglevel', CFFMPEG_LEGLEVEL,
        '-dump_attachment:t', '', '-i', file_path
    )

    print('Attachment dump:')  # , ' '.join(cmd))

    return subprocess.call(cmd, cwd=dst_dir)


def get_video_stream(media, width, height, codec, start_time, subtitle_index):
    file_path = os.path.join(media.parent().path(), media.file_path())
    if not os.path.exists(file_path):
        return None, None

    stream_lines = [line for line in _get_stream_info(file_path) if (
        "Stream" in line and "Video" in line
    )]
    w, h = _get_width_height(stream_lines, width, height)

    if not codec:
        is_h264 = "Video: h264" in stream_lines[0]
        is_vp8 = "Video: vp8" in stream_lines[0]
        is_vp9 = "Video: vp9" in stream_lines[0]

        if is_h264:
            mime = ".mp4"
        elif is_vp8 or is_vp9:
            mime = ".webm"

        if not mime:
            return None, None

        dst_path = os.path.join(CTMP_DIR, f'{media.id()}-video{mime}')

        if not os.path.exists(dst_path):
            os.makedirs(os.path.dirname(dst_path), exist_ok=True)
            if _video_dump(file_path, start_time, dst_path) != 0:
                return None, None

        stream, mime = dst_path, mime
    else:
        stream, mime = _video_stream(
            file_path, codec, w, h, start_time, subtitle_index
        )

    return stream, mime


def get_audio_stream(media, stream_index, codec, start_time):
    file_path = os.path.join(media.parent().path(), media.file_path())
    if not os.path.exists(file_path):
        return None, None

    if not codec:
        stream_lines = _get_stream_info(file_path)
        re_sub_audio = re.compile(R_SUB_AUDIO)

        for line in [line for line in stream_lines if "Audio" in line]:
            info = re_sub_audio.search(line)
            _stream_index = info.group(1) if info else None
            if _stream_index != stream_index:
                continue

            is_aac = "Audio: aac" in line
            is_flac = "Audio: flac" in line
            is_opus = "Audio: opus" in line
            is_vorbis = "Audio: vorbis" in line
            break

        if is_aac:
            mime = ".aac"
            format = "adts"
        elif is_flac:
            mime = ".flac"
            format = "flac"
        elif is_opus:
            mime = ".opus"
            format = "opus"
        elif is_vorbis:
            mime = ".vorbis"
            format = "oga"

        if not mime:
            return None, None

        dst_path = os.path.join(
            CTMP_DIR, f'{media.id()}-audio-{stream_index}{mime}'
        )

        if not os.path.exists(dst_path):
            os.makedirs(os.path.dirname(dst_path), exist_ok=True)
            if _audio_dump(
                file_path, stream_index, start_time, format, dst_path
            ) != 0:
                return None, None

        ffmpeg_cmd = dst_path
    else:
        if codec == "vorbis":
            format = "oga"
            audio_codec = "libvorbis"
            mime = ".vorbis"
        else:
            format = "opus"
            audio_codec = "libopus"
            mime = ".opus"

        ffmpeg_cmd = _audio_stream(
            file_path, stream_index, start_time, format, audio_codec
        )

    return ffmpeg_cmd, mime


def get_subtitle(media, type, index):
    if type not in ("internal", "external"):
        return None, None

    if type == "internal":
        file_path = os.path.join(media.parent().path(), media.file_path())
    elif type == "external":
        file_path = os.path.join(
            media.parent().path(), media.subtitles[int(index)]
        )

    if not os.path.exists(file_path):
        return None, None

    stream_index = None
    is_ass = False

    if type == "internal":
        stream_lines = _get_stream_info(file_path)
        re_sub_audio = re.compile(R_SUB_AUDIO)

        for line in [line for line in stream_lines if "Subtitle" in line]:
            info = re_sub_audio.search(line)
            if info and info.group(1) == index:
                is_ass = "Subtitle: ass" in line
                break

        stream_index = index

    elif type == "external":
        is_ass = file_path.endswith(".ass")
        stream_index = None

    if is_ass:
        mime = ".ass"
        format = "ass"
    else:
        mime = ".vtt"
        format = "webvtt"

    ffmpeg_cmd = _subtitle(file_path, stream_index, format)

    return ffmpeg_cmd, mime


def get_font(media, font_name):
    dst_path = os.path.join(
        CTMP_DIR,
        media.id(),
        "fonts",
        font_name
    )

    if os.path.exists(dst_path):
        return dst_path

    if "%20" in dst_path:
        if os.path.exists(dst_path.replace("%20", " ")):
            return dst_path.replace("%20", " ")

    file_path = os.path.join(media.parent().path(), media.file_path())
    if not os.path.exists(file_path):
        return None

    from pathlib import Path
    Path(dst_path).parent.mkdir(parents=True, exist_ok=True)

    exit_code = _dump_attachments(file_path, os.path.dirname(dst_path))

    if os.path.exists(dst_path):
        return dst_path

    if "%20" in dst_path:
        if os.path.exists(dst_path.replace("%20", " ")):
            return dst_path.replace("%20", " ")

    return None


def get_streams(media, width, height, decoders, start_time):
    file_path = os.path.join(media.parent().path(), media.file_path())
    if not os.path.exists(file_path):
        return None

    streams = []
    audio = []
    subtitles = []
    fonts = []

    media_id = media.id()

    stream_lines = _get_stream_info(file_path)

    for line in [line for line in stream_lines if "Video" in line]:
        is_h264 = "Video: h264" in line
        is_vp8 = "Video: vp8" in line
        is_vp9 = "Video: vp9" in line
        break

    if is_h264 and "h264" in decoders:
        transcode = None
    elif is_vp8 and "vp8" in decoders:
        transcode = None
    elif is_vp9 and "vp9" in decoders:
        transcode = None
    elif "vp9" in decoders:
        transcode = "vp9"
    else:
        transcode = "vp8"

    if transcode:
        print(line)

    if ALWAYS_TRANSCODE_VIDEO:
        transcode = "vp9"

    if CFFMPEG_STREAM:
        streams.append(f"http://{CFFMPEG_HOST}:{CFFMPEG_PORT}/video.webm")
        cmd, mime = get_video_stream(
            media, width, height, "vp9", start_time, None
        )
        print(' '.join(cmd))
        subprocess.Popen(cmd)
    else:
        video_url = f'/video/{width}/{height}/{media_id}?start={start_time}'

        if transcode:
            streams.append(f'{video_url}&transcode={transcode}')
        else:
            streams.append(video_url)
            streams.append(f'{video_url}&transcode=vp9')

    re_sub_audio = re.compile(R_SUB_AUDIO)

    for line in [line for line in stream_lines if "Audio" in line]:
        info = re_sub_audio.search(line)
        stream_index = info.group(1) if info else None
        if not stream_index:
            continue

        lang = info.group(2) if info else None

        is_default = "(default)" in line
        is_forced = "(forced)" in line
        is_aac = "Audio: aac" in line
        is_flac = "Audio: flac" in line
        is_opus = "Audio: opus" in line
        is_vorbis = "Audio: vorbis" in line

        if is_aac and "aac" in decoders:
            transcode = None
        elif is_flac and "flac" in decoders:
            transcode = None
        elif is_opus and "opus" in decoders:
            transcode = None
        elif is_vorbis and "vorbis" in decoders:
            transcode = None
        elif "opus" in decoders:
            transcode = "opus"
        else:
            transcode = "vorbis"

        if transcode:
            print(line)

        if ALWAYS_TRANSCODE_AUDIO:
            transcode = "opus"

        sources = []
        audio_url = f"/audio/{stream_index}/{media_id}?start={start_time}"

        if transcode:
            sources.append(f'{audio_url}&transcode={transcode}')
        else:
            sources.append(audio_url)
            sources.append(f'{audio_url}&transcode=opus')

        _audio = {
            'id': stream_index,
            'src': sources,
            'lang': lang,
            'is_forced': is_forced,
            'default': is_default
        }

        if is_default:
            audio.insert(0, _audio)
        else:
            audio.append(_audio)

    if len(audio) and audio[0]['default'] is not True:
        audio[0]['default'] = True

    for line in [line for line in stream_lines if "Subtitle" in line]:
        is_bitmap = any([
            "Subtitle: dvd_subtitle" in line,
            "Subtitle: hdmv_pgs_subtitle" in line
        ])
        if is_bitmap:
            continue
            pass

        is_default = "(default)" in line
        is_forced = "(forced)" in line
        is_ass = "Subtitle: ass" in line

        info = re_sub_audio.search(line)
        stream_index = info.group(1) if info else None
        lang = info.group(2) if info else "Unknown"
        src = f'/subtitle/internal/{stream_index}/{media_id}'

        if is_ass:
            src = f"{src}.ass"
        elif is_bitmap:
            src = f"{src}.tra"
        else:
            src = f"{src}.vtt"

        subtitle = {
            'src': src,
            'lang': lang,
            'default': is_default,
            'forced': is_forced,
            'requires_transcode': is_bitmap
        }

        if stream_index:
            subtitles.append(subtitle)

    for i in range(len(media.subtitles)):
        src = f'/subtitle/external/{i}/{media_id}'
        is_ass = media.subtitles[i].endswith(".ass")
        src = src + (".ass" if is_ass else ".vtt")
        subtitles.append({
            'src': src,
            'lang': "External",
            'default': False,
            'forced': False
        })

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
            fonts.append(f"/fonts/{media_id}/{filename.group(1)}")

    return {
        'id': media_id,
        'streams': streams,
        'audio': audio,
        'subtitles': subtitles,
        'duration': duration,
        'fonts': fonts,
        'start_time': start_time
    }
