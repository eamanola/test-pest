import sys
import os
import subprocess
import re
import time

from classes.ffmpeg import FFMpeg, FFProbe

from CONFIG import (
    CFFMPEG_STREAM, CFFMPEG_HOST, CFFMPEG_PORT, CFFMPEG_LEGLEVEL, CTMP_DIR,
    CENABLE_BITMAPSUBS
)

ALWAYS_TRANSCODE = False
ALWAYS_TRANSCODE_AUDIO = ALWAYS_TRANSCODE
ALWAYS_TRANSCODE_VIDEO = ALWAYS_TRANSCODE


def _subtitle(file_path, stream_index, format):
    cmd = FFMpeg().y().log().input(file_path).format(format)

    if stream_index is not None:
        cmd.map(f'0:{stream_index}')

    cmd.output('pipe:1')

    print('Subtitle:')  # , ' '.join(cmd.cmd))

    return cmd.cmd


def _dump_attachments(file_path, dst_dir):
    cmd = FFMpeg().n().log().dump_attachment().input(file_path)

    print('Attachment dump:')  # , ' '.join(cmd.cmd))

    return subprocess.call(cmd.cmd, cwd=dst_dir)


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
            internal_sub_len = len_streams(file_path)

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
    probe = FFProbe().log().of("default=noprint_wrappers=1:nokey=1") \
        .input(file_path).stream(["codec_name"]).select_streams("v:0")

    probe_proc = subprocess.Popen(probe.cmd, stdout=subprocess.PIPE)
    probe_proc.wait()
    codec_name = probe_proc.stdout.read().decode("utf8").strip()

    if codec_name == "h264":
        mime = ".mp4"
        format = "mp4"
    elif codec_name in ("vp8", "vp9"):
        mime = ".webm"
        format = "webm"
    else:
        mime = None
        format = None

    return mime, format


def get_audio_info(file_path, stream_index):
    probe = FFProbe().log().of("default=noprint_wrappers=1:nokey=1") \
        .input(file_path).stream(["codec_name"]) \
        .select_streams(str(stream_index))

    probe_proc = subprocess.Popen(probe.cmd, stdout=subprocess.PIPE)
    probe_proc.wait()
    codec_name = probe_proc.stdout.read().decode("utf8").strip()

    if codec_name == "aac":
        mime = ".aac"
        format = "adts"
    elif codec_name == "flac":
        mime = ".flac"
        format = "flac"
    elif codec_name == "opus":
        mime = ".opus"
        format = "opus"
    elif codec_name == "vorbis":
        mime = ".vorbis"
        format = "oga"
    else:
        mime = None
        format = None

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
        return None, None, None

    if video_index is None and audio_index is None:
        return None, None, None

    if subtitle_index is not None:
        # ffmpeg -y -i input.mkv -filter_complex '[v:0][0:s:0]overlay' \
        # -c:v libx264 -movflags +faststart -f 'matroska' -map 0:a \
        # -c:a copy pipe:1|vlc -
        # ffmpeg -y -i input.mkv -filter_complex '[v:0][0:s:0]overlay' \
        # -f h264 pipe:1| ffmpeg -i input.mkv -i pipe:0 -map 0:a -map 1 \
        # -quality realtime -speed 10 -f webm pipe:1|vlc -

        prep_cmd = FFMpeg().y().log(stats=True).input(file_path) \
            .filter_complex(f'[0:v:0][0:{subtitle_index}]overlay') \
            .format("h264")

        prep_cmd.cmd = prep_cmd.cmd + ["-threads", "2"]
        prep_cmd.cmd = prep_cmd.cmd + ["-preset", "veryfast"]
        prep_cmd.output("pipe:1")

        vcodec = "vp9"
        if audio_index:
            acodec = "opus"

        input_cmd = prep_cmd.cmd
    else:
        input_cmd = None
    ###########################################################################

    cmd, mime = None, None

    if disable_re:
        use_re = False
    else:
        use_re = (
            vcodec is not None
            or acodec is not None
        ) and input_cmd is None

    cmd = FFMpeg().y().log() \
        .input(file_path, re=use_re)
    if input_cmd:
        cmd.input("pipe:0")

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

        if input_cmd:
            cmd.map("1")
        else:
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

    dst_path = os.path.join(CTMP_DIR, media.id(), "-".join(dst_file) + mime)

    if vcodec is None and acodec is None:
        if os.path.exists(dst_path):
            return dst_path, mime, None

    ###########################################################################

    success, cmd.cmd = test_cmd(cmd.cmd, media.id())
    if not success:
        print("test fail")
        return None, None, None

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

    return ret, mime, input_cmd


def test_cmd(cmd, media_id):
    passed = False

    import uuid

    tmp_file = os.path.join(
        CTMP_DIR, media_id, str(uuid.uuid1())
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

            return test_cmd(cmd, media_id)

        if any((
            "in MP4 support is experimental" in line
        ) for line in stderr_str.split("\n")):
            print("Adding -strict experimental")
            cmd.append('-strict')
            cmd.append('experimental')

            return test_cmd(cmd, media_id)

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
    start_time = round(start_time, 3)

    ###########################################################################

    dst_path = os.path.join(
        CTMP_DIR, media.id(), 'trimmed', str(start_time)
    )
    if os.path.exists(dst_path):
        return dst_path

    os.makedirs(os.path.dirname(dst_path), exist_ok=True)

    ###########################################################################

    previous_trims = os.listdir(os.path.dirname(dst_path))

    usable_trim = None
    for previous_trim in previous_trims:
        previous_trim = float(previous_trim)
        if previous_trim < start_time:
            if usable_trim is None or previous_trim > usable_trim:
                usable_trim = previous_trim

    if usable_trim is None:
        file_path = os.path.join(media.parent().path(), media.file_path())
        if not os.path.exists(file_path):
            return None
    else:
        print('Using previous trim', usable_trim)
        file_path = os.path.join(os.path.dirname(dst_path), str(usable_trim))
        start_time = start_time - usable_trim

    ###########################################################################

    cmd = FFMpeg().y().log(stats=True).input(file_path, ss=start_time)

    if usable_trim is None:
        for subtitle in media.subtitles:
            cmd.input(
                os.path.join(media.parent().path(), subtitle), ss=start_time
            )

    cmd.map('0')

    if usable_trim is None:
        for index in range(0, len(media.subtitles)):
            cmd.map(str(index + 1))

    cmd.acodec('copy').vcodec('copy').scodec('copy').copyts() \
        .format('matroska').output(dst_path)

    ###########################################################################

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
    chapters = []

    media_id = media.id()

    font_dir = os.path.join(CTMP_DIR, media.id(), "fonts")
    os.makedirs(font_dir, exist_ok=True)
    _dump_attachments(file_path, font_dir)

    probe = FFProbe().log().of().input(file_path).duration() \
        .stream(["index", "duration", "codec_name", "codec_type"]) \
        .stream_tags(["language", "title", "filename"]) \
        .stream_disposition(["default", "forced"]) \
        .chapters()

    probe_json = get_json(probe)

    if "streams" in probe_json.keys():
        for stream in probe_json["streams"]:
            ################################################################
            if stream["codec_type"] == "video":
                type = None
                codec_name = stream["codec_name"]
                if codec_name == "h264":
                    type = 'video/mp4; codecs="avc1.42E01E"'
                elif codec_name == "vp8":
                    type = 'video/webm; codecs="vp8"'
                elif codec_name == "vp9":
                    type = 'video/webm; codecs="vp9"'
                else:
                    type = "Unsupported"
                    print("Unsupported Video codec_name:", codec_name)

                video.append({
                    "type": type
                })
            ################################################################
            elif stream["codec_type"] == "audio":
                lang = None
                title = None
                if "tags" in stream.keys():
                    if "language" in stream["tags"].keys():
                        lang = stream["tags"]["language"]

                    if "title" in stream["tags"].keys():
                        title = stream["tags"]["title"]

                default = False
                forced = False
                if "disposition" in stream.keys():
                    if "default" in stream["disposition"].keys():
                        default = stream["disposition"]["default"] == 1

                    if "forced" in stream["disposition"].keys():
                        forced = stream["disposition"]["forced"] == 1

                type = None
                codec_name = stream["codec_name"]
                if codec_name == "aac":
                    type = 'audio/aac'
                elif codec_name == "flac":
                    type = 'audio/ogg; codecs=flac'
                elif codec_name == "opus":
                    type = 'audio/ogg; codecs=opus'
                elif codec_name == "vorbis":
                    type = 'audio/ogg; codecs="vorbis"'
                else:
                    type = "Unsupported"
                    print("Unsupported Audio codec_name:", codec_name)

                _audio = {
                    'id': stream["index"],
                    'lang': lang,
                    'title': title,
                    'is_forced': forced,
                    'default': default,
                    'type': type
                }

                if default:
                    audio.insert(0, _audio)
                else:
                    audio.append(_audio)

            if len(audio) and audio[0]['default'] is not True:
                audio[0]['default'] = True
            ################################################################
            elif stream["codec_type"] == "subtitle":
                codec_name = stream["codec_name"]
                is_bitmap = codec_name in ("dvd_subtitle", "hdmv_pgs_subtitle")
                if is_bitmap:
                    if not CENABLE_BITMAPSUBS:
                        print('Discard bitmap sub')
                        continue

                lang = None
                title = None
                if "tags" in stream.keys():
                    if "language" in stream["tags"].keys():
                        lang = stream["tags"]["language"]

                    if "title" in stream["tags"].keys():
                        title = stream["tags"]["title"]

                default = False
                forced = False
                if "disposition" in stream.keys():
                    if "default" in stream["disposition"].keys():
                        default = stream["disposition"]["default"] == 1

                    if "forced" in stream["disposition"].keys():
                        forced = stream["disposition"]["forced"] == 1

                is_ass = codec_name == "ass"

                src = f'/subtitle/internal/{stream["index"]}/{media_id}'
                if is_ass:
                    src = f"{src}.ass"
                elif is_bitmap:
                    src = f"{src}.tra"
                else:
                    src = f"{src}.vtt"

                subtitle = {
                    'src': src,
                    'lang': lang,
                    'title': title,
                    'default': default,
                    'forced': forced,
                    'requires_transcode': is_bitmap
                }
                subtitles.append(subtitle)
            ################################################################
            elif stream["codec_type"] == "attachment":
                if stream["codec_name"] == "ttf":
                    if (
                        "tags" in stream.keys()
                        and "filename" in stream["tags"]
                    ):
                        filename = stream['tags']['filename']
                        if os.path.exists(os.path.join(font_dir, filename)):
                            fonts.append(f"/fonts/{media_id}/{filename}")

    ###########################################################################

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
    if "format" in probe_json.keys():
        if "duration" in probe_json["format"].keys():
            duration = int(float(probe_json["format"]["duration"]))

    ###########################################################################

    if "chapters" in probe_json.keys():
        for chapter in probe_json["chapters"]:
            start_time = None
            end_time = None
            title = ""
            if "start_time" in chapter.keys():
                start_time = float(chapter["start_time"])
            if "end_time" in chapter.keys():
                end_time = float(chapter["end_time"])
            if "tags" in chapter.keys():
                if "title" in chapter["tags"]:
                    title = chapter["tags"]["title"]
            chapters.append({
                'title': title,
                'start_time': start_time,
                'end_time': end_time
            })

    return {
        'id': media_id,
        'video': video,
        'audio': audio,
        'subtitles': subtitles,
        'duration': duration,
        'fonts': fonts,
        'chapters': chapters
    }


def get_json(probe):
    probe_proc = subprocess.Popen(probe.cmd, stdout=subprocess.PIPE)
    probe_proc.wait()

    import json
    return json.load(probe_proc.stdout)


def len_streams(file_path):
    from classes.ffmpeg import FFProbe
    probe = FFProbe().log().of().input(file_path).stream(["index"])

    # print(' '.join(probe.cmd))
    probe_json = get_json(probe)

    return len(probe_json["streams"]) if "streams" in probe_json.keys() else 0
