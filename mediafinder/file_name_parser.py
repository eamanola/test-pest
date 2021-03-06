import os
import re


class File_name_parser(object):
    r_oad = r"OAD"
    re_oad = re.compile(r_oad)

    r_ncop = r"NCOP"
    re_ncop = re.compile(r_ncop)

    r_nced = r"NCED"
    re_nced = re.compile(r_nced)

    r_extra = "EXTRA"
    re_extra = re.compile(r_extra, re.IGNORECASE)

    r_ova = "OVA"
    re_ova = re.compile(r_ova)

    r_episode = r"(?:episode|e|ep)"
    r_episode2 = (
        r"(?:^|[^a-zA-Z0-9]+)(?:\s*)(\d{1,3})(?:v\d+)?(?:[^a-zA-Z0-9]+|$)"
    )

    r_episode_prefix = r"(?:^|[^a-zA-Z]+)"
    r_episode_num = r"(?:\s*|\.)(\d+)(?:v\d+)?"
    r_episode_postfix = r"(?:$|\s|\.)"

    r_season_prefix = r"(?:^|[^a-zA-Z0-9]+)"
    r_season_num = r"(?:\s*|\.)(\d+)"
    r_season = r"(?:season(?:s?)|s)"
    r_season_full = r_season_prefix + r_season + r_season_num

    re_season = re.compile(r_season_full, re.IGNORECASE)

    re_episode_oad = re.compile(
        r_episode_prefix + r_oad + r_episode_num + r_episode_postfix
    )
    re_episode_ncop = re.compile(
        r_episode_prefix + r_ncop + r_episode_num + r_episode_postfix
    )
    re_episode_nced = re.compile(
        r_episode_prefix + r_nced + r_episode_num + r_episode_postfix
    )
    re_episode_ova = re.compile(
        r_episode_prefix + r_ova + r_episode_num + r_episode_postfix
    )
    re_episode_extra = re.compile(
        r_episode_prefix + r_extra + r_episode_num + r_episode_postfix,
        re.IGNORECASE
    )
    re_episode = re.compile(
        r_episode_prefix + r_episode + r_episode_num + r_episode_postfix,
        re.IGNORECASE
    )
    re_episode2 = re.compile(
        r_episode2,
        re.IGNORECASE
    )

    re_metatags = re.compile(r"\([^\)]*\)\s*")
    re_usertags = re.compile(r"\[[^\]]*\]\s*")

    r_year1 = r"\((\d{4})\)"
    r_year2 = r"\[(\d{4})\]"
    r_year3 = r"(?:\s+|\.|^)(\d{4})(?:\s+|\.|$)"
    re_year = re.compile(
        r"\s*(?:" + r_year1 + r"|" + r_year2 + r"|" + r_year3 + r")\s*"
    )

    r_info_sep = r"(?:\s+|\.|-|$)"
    re_clean_show_name = (
        re.compile(r"(?:720|1080)p" + r_info_sep, re.IGNORECASE),
        # re.compile("720p(?:\s+|\.|-|$)", re.IGNORECASE),

        re.compile(r"(?:web|hd|bd)rip" + r_info_sep, re.IGNORECASE),
        # re.compile("hdrip(?:\s+|\.|$)", re.IGNORECASE),
        re.compile(r"web-dl" + r_info_sep, re.IGNORECASE),

        re.compile(r"\d+mb" + r_info_sep, re.IGNORECASE),

        re.compile(r"x26(?:4|5)" + r_info_sep, re.IGNORECASE),
        re.compile(r"hvec" + r_info_sep, re.IGNORECASE),
        re.compile(r"xvid" + r_info_sep, re.IGNORECASE),
        re.compile(r"aac" + r_info_sep, re.IGNORECASE),
        re.compile(r"ac3(?:.?(?:evo))?" + r_info_sep, re.IGNORECASE),
        re.compile(r"aac5.1" + r_info_sep, re.IGNORECASE),
        re.compile("flac" + r_info_sep, re.IGNORECASE),
        re.compile("BluRay" + r_info_sep, re.IGNORECASE),

        re.compile(r_season_full + r"(?:[^\s\.]*|$)", re.IGNORECASE),
        re_year,

        re.compile(r"\."),
        re.compile(r"\s+")

    )

    UNKNOWN_SEASON = 0
    UNKNOWN_EPISODE = 0
    UNKNOWN_YEAR = None
    MEDIA_EXTENSIONS = ('.mkv', '.mp4', '.avi', '.m4v')
    SUBTITLE_EXTENSIONS = ('.srt', '.ass')
    SUBTITLE_LANGS = ('.en',)
    FILE_EXTENSIONS = MEDIA_EXTENSIONS + SUBTITLE_EXTENSIONS

    @staticmethod
    def clean_show_name(show_name):
        for clean in File_name_parser.re_clean_show_name:
            show_name = clean.sub(" ", show_name)

        return show_name

    @staticmethod
    def guess_show_name(file):
        parts = [part for part in file.split(os.path.sep) if part.strip()]

        if len(parts) == 1:
            show_name = parts[0]
        else:
            parts.reverse()
            parts.pop(0)

            show_name = None

            for part in parts:
                if (
                    not File_name_parser.guess_season(part)
                    and not File_name_parser.guess_episode(part)
                    and not File_name_parser.is_extra(part)
                    and re.search(r'[a-zA-Z]', part)
                ):
                    show_name = part
                    break

            if show_name is None:
                show_name = parts[-1]

        show_name = File_name_parser.remove_tags(show_name)
        show_name = File_name_parser.remove_file_extension(show_name)
        show_name = File_name_parser.clean_show_name(show_name)

        show_name = show_name.replace(".", " ").strip()

        return show_name

    @staticmethod
    def guess_season(file):
        parts = file.split(os.path.sep)
        parts.reverse()

        season = File_name_parser.UNKNOWN_SEASON

        for part in parts:
            has_season = File_name_parser.re_season.search(part)

            if has_season:
                season = has_season.group(1)
                break

        return int(season)

    @staticmethod
    def guess_episode(file):
        parts = File_name_parser.remove_tags(file).split(os.path.sep)
        parts.reverse()

        episode = File_name_parser.UNKNOWN_EPISODE

        for part in parts:
            for reg in [
                File_name_parser.re_episode,
                File_name_parser.re_episode_extra,
                File_name_parser.re_episode_oad,
                File_name_parser.re_episode_ncop,
                File_name_parser.re_episode_nced,
                File_name_parser.re_episode_ova
            ]:
                has_episode = reg.search(part)
                if has_episode:
                    episode = has_episode.group(1)
                    break

            if episode != File_name_parser.UNKNOWN_EPISODE:
                break

        if episode == File_name_parser.UNKNOWN_EPISODE and len(parts) > 1:
            has_episode = File_name_parser.re_episode2.search(
                File_name_parser.clean_show_name(parts[0])
            )
            if has_episode:
                episode = has_episode.group(1)

                # check if number is related to a movie
                has_episode_folder = File_name_parser.re_episode2.search(
                    File_name_parser.clean_show_name(parts[1])
                )
                if has_episode_folder:
                    if episode == has_episode_folder.group(1):
                        print('A movie with number?', file)
                        episode = File_name_parser.UNKNOWN_EPISODE

        return int(episode)

    @staticmethod
    def guess_year(file):
        parts = file.split(os.path.sep)

        year = File_name_parser.UNKNOWN_YEAR

        for part in parts:
            has_year = File_name_parser.re_year.search(part)

            if has_year:
                if has_year.group(1):
                    year = has_year.group(1)
                elif has_year.group(2):
                    year = has_year.group(2)
                elif has_year.group(3):
                    year = has_year.group(3)
                else:
                    year = File_name_parser.UNKNOWN_YEAR
                break
        return int(year) if year else None

    @staticmethod
    def remove_tags(file):
        return File_name_parser.remove_user_tags(
            File_name_parser.remove_meta_tags(file)
        )

    @staticmethod
    def remove_user_tags(file):
        return File_name_parser.re_usertags.sub("",  file)

    @staticmethod
    def remove_meta_tags(file):
        return File_name_parser.re_metatags.sub("", file)

    @staticmethod
    def remove_file_extension(file):
        extension_removed = file

        file_name, extension = os.path.splitext(file)
        if extension in File_name_parser.FILE_EXTENSIONS:
            extension_removed = file_name

            if File_name_parser.is_subtitle(file):
                file_name, extension = os.path.splitext(extension_removed)
                if extension in File_name_parser.SUBTITLE_LANGS:
                    extension_removed = file_name

        return extension_removed

    @staticmethod
    def is_media(file):
        file_name, extension = os.path.splitext(file)
        return extension in File_name_parser.MEDIA_EXTENSIONS

    @staticmethod
    def is_subtitle(file):
        file_name, extension = os.path.splitext(file)
        return extension in File_name_parser.SUBTITLE_EXTENSIONS

    @staticmethod
    def is_extra(file):
        file_removed_tags = File_name_parser.remove_tags(file)
        return (
            File_name_parser.re_extra.search(file_removed_tags) is not None or
            File_name_parser.is_oad(file) or
            File_name_parser.is_ncop(file) or
            File_name_parser.is_nced(file) or
            File_name_parser.is_ova(file)
        )

    @staticmethod
    def is_oad(file):
        file_removed_tags = File_name_parser.remove_tags(file)
        return File_name_parser.re_oad.search(file_removed_tags) is not None

    @staticmethod
    def is_ncop(file):
        file_removed_tags = File_name_parser.remove_tags(file)
        return File_name_parser.re_ncop.search(file_removed_tags) is not None

    @staticmethod
    def is_nced(file):
        file_removed_tags = File_name_parser.remove_tags(file)
        return File_name_parser.re_nced.search(file_removed_tags) is not None

    @staticmethod
    def is_ova(file):
        file_removed_tags = File_name_parser.remove_tags(file)
        return File_name_parser.re_ova.search(file_removed_tags) is not None
