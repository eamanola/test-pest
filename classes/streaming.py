import sys
import os
import subprocess
import re
import time

from classes.ffmpeg import FFMpeg

from CONFIG import (
    CFFMPEG_STREAM, CFFMPEG_HOST, CFFMPEG_PORT, CFFMPEG_LEGLEVEL, CTMP_DIR
)

R_SUB_AUDIO = r'.*Stream\ #0:([0-9]+)(?:\(([a-zA-Z]{3})\))?.*'
R_DURATION = r'.*Duration\:\ (\d\d)\:(\d\d)\:(\d\d).*'

ALWAYS_TRANSCODE = False
ALWAYS_TRANSCODE_AUDIO = ALWAYS_TRANSCODE
ALWAYS_TRANSCODE_VIDEO = ALWAYS_TRANSCODE


def _get_stream_info(file_path):
    cmd = FFMpeg().log(loglevel=None).input(file_path).cmd

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


def _subtitle(file_path, stream_index, format):
    cmd = FFMpeg().y().log().input(file_path).format(format)

    if stream_index is not None:
        cmd.map(f'0:{stream_index}')

    cmd.output('pipe:1')

    print('Subtitle:')  # , ' '.join(cmd))

    return cmd.cmd


def _dump_attachments(file_path, dst_dir):
    cmd = FFMpeg().n().log().dump_attachment().input(file_path).cmd

    print('Attachment dump:')  # , ' '.join(cmd))

    return subprocess.call(cmd, cwd=dst_dir)


def get_subtitle(media, type, index, format, start_time):
    if type not in ("internal", "external"):
        return None, None

    ##########################################################################

    file_path = os.path.join(media.parent().path(), media.file_path())
    if not os.path.exists(file_path):
        return None, None

    ##########################################################################

    if start_time:
        if type == "external":
            stream_lines = _get_stream_info(file_path)
            internal_sub_len = len([
                line for line in stream_lines if "Subtitle" in line
            ])

            type = "internal"
            index = int(index) + internal_sub_len

        file_path = trim(media, start_time)

    ##########################################################################

    if type == "external":
        file_path = os.path.join(
            media.parent().path(), media.subtitles[int(index)]
        )
        if not os.path.exists(file_path):
            return None, None

        index = None

    ##########################################################################

    if format == "ass":
        mime = ".ass"
        _format = "ass"
    else:  # elif format == "vtt":
        mime = ".vtt"
        _format = "webvtt"

    ffmpeg_cmd = _subtitle(file_path, index, _format)

    return ffmpeg_cmd, mime


def get_font(media, font_name):
    dst_path = os.path.join(
        CTMP_DIR, media.id(), "fonts", font_name
    )

    if os.path.exists(dst_path):
        return dst_path

    return None


def get_video_info(file_path):
    stream_lines = [line for line in _get_stream_info(file_path) if (
        "Stream" in line and "Video" in line
    )]

    if "Video: h264" in stream_lines[0]:
        mime = ".mp4"
        format = "mp4"
    elif "Video: vp8" in stream_lines[0] or "Video: vp9" in stream_lines[0]:
        mime = ".webm"
        format = "webm"
    else:
        mime = None
        format = None

    return mime, format


def get_audio_info(file_path, stream_index):
    stream_lines = _get_stream_info(file_path)
    re_sub_audio = re.compile(R_SUB_AUDIO)

    for line in [line for line in stream_lines if "Audio" in line]:
        info = re_sub_audio.search(line)
        _stream_index = info.group(1) if info else None
        if _stream_index != str(stream_index):
            continue

        if "Audio: aac" in line:
            mime = ".aac"
            format = "adts"
        elif "Audio: flac" in line:
            mime = ".flac"
            format = "flac"
        elif "Audio: opus" in line:
            mime = ".opus"
            format = "opus"
        elif "Audio: vorbis" in line:
            mime = ".vorbis"
            format = "oga"
        else:
            mime = None
            format = None

        break

    return mime, format


def av(
    media, video_index, vcodec, audio_index, acodec,
    start_time, width, height, subtitle_index, disable_re=False
):
    if start_time:
        file_path = trim(media, start_time)
    else:
        file_path = os.path.join(
            media.parent().path(), media.file_path()
        )

    if not os.path.exists(file_path):
        return None, None

    if video_index is None and audio_index is None:
        return None, None

    if subtitle_index:
        input = file_path
        file_path = os.path.join(
            CTMP_DIR,
            media.id(),
            "sub-included",
            f"{subtitle_index}.mkv"
        )
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        prep_cmd = FFMpeg().y().log(stats=True).input(input) \
            .filter_complex(f'[0:v:0][0:{subtitle_index}]overlay') \
            .vcodec("h264")

        vcodec = "vp9"

        if audio_index:
            prep_cmd.map(f'0:{audio_index}').acodec('copy')

            audio_index = 1
            acodec = "opus"

        prep_cmd.cmd.append("-threads")
        prep_cmd.cmd.append("2")
        prep_cmd.cmd.append("-preset")
        prep_cmd.cmd.append("veryfast")
        prep_cmd.format('matroska').output(file_path)

        subprocess.Popen(prep_cmd.cmd)
        time.sleep(5)

        print(" ".join(prep_cmd.cmd))

    ###########################################################################

    cmd, mime = None, None

    if disable_re:
        use_re = False
    else:
        use_re = vcodec is not None or acodec is not None

    cmd = FFMpeg().y().log() \
        .input(file_path, re=use_re)

    ###########################################################################

    if video_index is not None:
        if vcodec is None:
            mime, format = get_video_info(file_path)
            cmd.vcodec('copy')
            cmd.format(format)

        elif vcodec in ("vp8", "vp9"):
            mime = ".webm"
            try:
                max_threads = int(len(os.sched_getaffinity(0)) / 2)
            except Exception:
                max_threads = int(os.cpu_count() / 2)
            cmd.webm(
                vcodec, width=width, height=height, max_threads=max_threads
            )
        else:
            print("AV: Unsupported video codec", vcodec)

        cmd.map(f'0:v:{video_index}')

    ###########################################################################

    if audio_index is not None:
        cmd.map(f'0:{audio_index}')

        if mime == ".webm":
            cmd.acodec("libopus")

        elif acodec is None:
            _mime, _format = get_audio_info(file_path, audio_index)
            cmd.acodec('copy')

        elif acodec == "vorbis":
            _mime = ".vorbis"
            _format = "oga"
            cmd.acodec("libvorbis")

        elif acodec == "opus":
            _mime = ".opus"
            _format = "opus"
            cmd.acodec("libopus")

        else:
            print("AV: Unsupported video codec", vcodec)

        if video_index is None:
            cmd.format(_format)
            mime = _mime

    ###########################################################################

    dst_file = [media.id()]
    if start_time:
        dst_file.append(str(start_time))
    if video_index:
        dst_file.append("v" + str(video_index))
    if audio_index:
        dst_file.append("a" + str(audio_index))
    if vcodec:
        dst_file.append("cv" + str(vcodec))
    if acodec:
        dst_file.append("ca" + str(acodec))

    dst_path = os.path.join(CTMP_DIR, "-".join(dst_file) + mime)

    if vcodec is None and acodec is None:
        if os.path.exists(dst_path):
            return dst_path, mime

    ###########################################################################

    success, cmd.cmd = test_cmd(cmd.cmd)
    if not success:
        return None, None

    ###########################################################################

    ret = None

    if vcodec is None and acodec is None:
        if not os.path.exists(dst_path):
            os.makedirs(os.path.dirname(dst_path), exist_ok=True)
            cmd.output(dst_path)

            dump_proc = subprocess.Popen(
                cmd.cmd,
                stderr=subprocess.PIPE,
                stdout=subprocess.DEVNULL
            )
            dump_proc.wait()
        ret = dst_path

    elif CFFMPEG_STREAM:
        stream_url = f'http://{CFFMPEG_HOST}:{CFFMPEG_PORT}/{dst_file}'
        cmd.cmd = cmd.cmd + [
            '-listen', '1',
            '-headers',
            'Cache-Control: private, must-revalidate, max-age=0',
            '-reconnect_streamed', '1',
            stream_url
        ]

        stream_proc = subprocess.Popen(cmd.cmd)

        ret = stream_url
    else:
        cmd.output('pipe:1')

        ret = cmd.cmd

    print("AV:")  # , " ".join(cmd.cmd))

    return ret, mime


def test_cmd(cmd):
    passed = False

    import uuid

    tmp_file = os.path.join(
        CTMP_DIR, str(uuid.uuid1())
    )
    os.makedirs(os.path.dirname(tmp_file), exist_ok=True)

    cmd_test = subprocess.Popen(
        cmd + [tmp_file],
        stderr=subprocess.PIPE,
        stdout=subprocess.DEVNULL
    )
    time.sleep(0.5)

    if cmd_test.poll() is not None and cmd_test.returncode == 1:
        stderr_str = cmd_test.stderr.read().decode("utf-8")

        # http://trac.ffmpeg.org/ticket/5718
        if any((
            "libopus" in line
            and "Invalid channel layout 5.1(side)" in line
        ) for line in stderr_str.split("\n")):
            print('Mapping channels manually')

            cmd.append("-af")
            cmd.append('aformat=channel_layouts=5.1|stereo')

            return test_cmd(cmd)

        if any((
            "in MP4 support is experimental" in line
        ) for line in stderr_str.split("\n")):
            print("Adding -strict experimental")
            cmd.append('-strict')
            cmd.append('experimental')

            return test_cmd(cmd)

        else:
            print("##################################################")
            print('Cmd test fail')
            print(" ".join(cmd))
            print("##################################################")
            print(stderr_str)
    else:
        cmd_test.terminate()
        passed = True

    return passed, cmd


def trim(media, start_time):
    file_path = os.path.join(media.parent().path(), media.file_path())
    if not os.path.exists(file_path):
        return None

    dst_path = os.path.join(
        CTMP_DIR, f'trimmed-{start_time}-{media.id()}.mkv'
    )
    if os.path.exists(dst_path):
        return dst_path

    os.makedirs(os.path.dirname(dst_path), exist_ok=True)

    cmd = FFMpeg().y().log(stats=True).input(file_path, ss=start_time)

    for subtitle in media.subtitles:
        cmd.input(
            os.path.join(media.parent().path(), subtitle), ss=start_time
        )

    cmd.map('0')

    for index in range(0, len(media.subtitles)):
        cmd.map(str(index + 1))

    cmd.acodec('copy').vcodec('copy').scodec('copy').copyts().output(dst_path)

    print('Trim:', ' '.join(cmd.cmd))

    proc = subprocess.Popen(cmd.cmd)
    proc.wait()

    return dst_path


def get_streams(media):
    file_path = os.path.join(media.parent().path(), media.file_path())
    if not os.path.exists(file_path):
        return None

    video = []
    audio = []
    subtitles = []
    fonts = []

    media_id = media.id()

    stream_lines = _get_stream_info(file_path)

    ###########################################################################

    for line in [line for line in stream_lines if "Video" in line]:
        if "Video: h264" in line:
            type = 'video/mp4; codecs="avc1.42E01E"'
        elif "Video: vp8" in line:
            type = 'video/webm; codecs="vp8"'
        elif "Video: vp9" in line:
            type = 'video/webm; codecs="vp9"'
        else:
            type = "Unsupported"
            print("Unsupported video type:\n", line)

    video.append({
        "type": type
    })

    ###########################################################################

    re_sub_audio = re.compile(R_SUB_AUDIO)

    for line in [line for line in stream_lines if "Audio" in line]:
        info = re_sub_audio.search(line)
        stream_index = info.group(1) if info else None
        if not stream_index:
            continue

        lang = info.group(2) if info else None

        is_default = "(default)" in line
        is_forced = "(forced)" in line
        if "Audio: aac" in line:
            type = 'audio/aac'
        elif "Audio: flac" in line:
            type = 'audio/ogg; codecs=flac'
        elif "Audio: opus" in line:
            type = 'audio/ogg; codecs=opus'
        elif "Audio: vorbis" in line:
            type = 'audio/ogg; codecs="vorbis"'
        else:
            type = "Unsupported"
            print("Unsupported audio type:\n", line)

        _audio = {
            'id': stream_index,
            'lang': lang,
            'is_forced': is_forced,
            'default': is_default,
            'type': type
        }

        if is_default:
            audio.insert(0, _audio)
        else:
            audio.append(_audio)

    if len(audio) and audio[0]['default'] is not True:
        audio[0]['default'] = True

    ###########################################################################

    for line in [line for line in stream_lines if "Subtitle" in line]:
        is_bitmap = any([
            "Subtitle: dvd_subtitle" in line,
            "Subtitle: hdmv_pgs_subtitle" in line
        ])
        if is_bitmap:
            print('Discard bitmap sub')
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

    ###########################################################################

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

    ###########################################################################

    font_dir = os.path.join(CTMP_DIR, media.id(), "fonts")
    os.makedirs(font_dir, exist_ok=True)
    _dump_attachments(file_path, font_dir)

    USE_ASS_JS = False

    re_attachment_names = re.compile(r"^\s*filename\s*\:\s*(.*)\s*$")
    for line in [
        line for line in stream_lines if (
            line.strip().startswith("filename")
            and line.strip().endswith((".otf", ".OTF", ".ttf", ".TTF"))
        )
    ]:
        filename = re_attachment_names.search(line)
        if filename:
            if USE_ASS_JS:
                font_path = os.path.join(font_dir, filename.group(1))
                if os.path.exists(font_path):
                    print(font_path)
                    font_proc = subprocess.Popen(
                        ['fc-scan', '-b', font_path],
                        stdout=subprocess.PIPE, text=True
                    )
                    font_proc.wait()
                    if font_proc.returncode == 0:
                        for line in font_proc.stdout.read().split("\n"):
                            if line.lstrip().startswith("family"):
                                family = line.replace("family:", "") \
                                    .replace("(s)", ",").replace("\"", "") \
                                    .strip().strip(",")
                                print(family)
                                break

                        fonts.append({
                            "family": family,
                            "url": f"/fonts/{media_id}/{filename.group(1)}"
                        })
            else:
                fonts.append(f"/fonts/{media_id}/{filename.group(1)}")

    return {
        'id': media_id,
        'video': video,
        'audio': audio,
        'subtitles': subtitles,
        'duration': duration,
        'fonts': fonts
    }
