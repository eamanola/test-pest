import os
import re

re_season = re.compile("(?:^|[^a-zA-Z]+)(?:season|s)(?:\s*|\.)(\d+)", re.IGNORECASE);
re_oad = re.compile("OAD");
re_ncop = re.compile("NCOP");
re_nced = re.compile("NCED");
re_extra = re.compile("extra", re.IGNORECASE);
re_episode_oad = re.compile("OAD(?:\s*|\.)(\d+)");
re_episode_ncop = re.compile("NCOP(?:\s*|\.)(\d+)");
re_episode_nced = re.compile("NCED(?:\s*|\.)(\d+)");
re_episode_extra = re.compile("extra(?:\s*|\.)(\d+)", re.IGNORECASE);
re_episode = re.compile("(?:^|[^a-zA-Z]+)(?:episode|e|ep)(?:\s*|\.)(\d+)", re.IGNORECASE);
re_episode2 = re.compile("(?:^|[^a-zA-Z0-9]+)(?:\s*)(\d{1,3})(?:[^a-zA-Z0-9]+|$)", re.IGNORECASE);
re_metatags = re.compile("\([^\)]*\)\s*");
re_year = re.compile("\s*(?:\((\d{4})\)|\[(\d{4})\]|(?:\s+|\.)(\d{4})(?:\s+|\.))\s*");
re_usertags = re.compile("\[[^\]]*\]\s*");
re_clean_show_name = (
    re.compile("(?:720|1080)p(?:\s+|\.|-|$)", re.IGNORECASE),
    #re.compile("720p(?:\s+|\.|-|$)", re.IGNORECASE),

    re.compile("(?:web|hd|bd)rip(?:\s+|\.|$)", re.IGNORECASE),
    #re.compile("hdrip(?:\s+|\.|$)", re.IGNORECASE),
    re.compile("web-dl(?:\s+|\.|$)", re.IGNORECASE),

    re.compile("\d+mb(?:\s+|\.|-|$)", re.IGNORECASE),

    re.compile("x26(?:4|5)(?:\s+|\.|-|$)", re.IGNORECASE),
    re.compile("hvec(?:\s+|\.|-|$)", re.IGNORECASE),
    re.compile("xvid(?:\s+|\.|-|$)", re.IGNORECASE),
    re.compile("aac(?:\s+|\.|-|$)", re.IGNORECASE),
    re.compile("ac3(?:.?(?:evo))?(?:\s+|\.|-|$)", re.IGNORECASE),
    re.compile("aac5.1(?:\s+|\.|-|$)", re.IGNORECASE),
    re.compile("flac", re.IGNORECASE),

    re.compile("\d{4}(?:\s+|\.|-|$)", re.IGNORECASE)
);

UNKNOWN_SEASON = 0;
UNKNOWN_EPISODE = 0;
UNKNOWN_YEAR = 0;
MEDIA_EXTENSIONS = ('.mkv', '.mp4','.avi');
SUB_TITLE_EXTENSIONS = ('.srt',);
FILE_EXTENSIONS = MEDIA_EXTENSIONS + SUB_TITLE_EXTENSIONS;

def clean_show_name(show_name):
    for clean in re_clean_show_name:
        show_name = clean.sub("", show_name);

    return show_name;

def guess_show_name(file):
    parts = file.split(os.path.sep)

    show_name = parts[0];
    show_name = remove_meta_tags(show_name)
    show_name = remove_user_tags(show_name)
    show_name = remove_file_extension(show_name)
    show_name = clean_show_name(show_name)

    show_name = show_name.replace(".", " ");

    return show_name.strip();

def guess_season(file):
    parts = file.split(os.path.sep);
    parts.reverse();

    season = UNKNOWN_SEASON;

    for part in parts:
        has_season = re_season.search(part);

        if has_season:
            season = has_season.group(1);
            break;

    return int(season);

def guess_episode(file):
    parts = remove_meta_tags(remove_user_tags(file)).split(os.path.sep);
    parts.reverse();

    episode = UNKNOWN_EPISODE;

    for part in parts:
        has_episode = re_episode.search(part);
        if has_episode:
            episode = has_episode.group(1);
            break;

        has_episode = re_episode_extra.search(part);
        if has_episode:
            episode = has_episode.group(1);
            break;

        has_episode = re_episode_oad.search(part);
        if has_episode:
            episode = has_episode.group(1);
            break;

        has_episode = re_episode_ncop.search(part);
        if has_episode:
            episode = has_episode.group(1);
            break;

        has_episode = re_episode_nced.search(part);
        if has_episode:
            episode = has_episode.group(1);
            break;
            
        has_episode = re_episode2.search(clean_show_name(part));
        if has_episode:
            episode = has_episode.group(1);
            break;

    return int(episode);

def guess_year(file):
    parts = file.split(os.path.sep);

    year = UNKNOWN_YEAR;

    for part in parts:
        has_year = re_year.search(part);

        if has_year:
            if has_year.group(1):
                year = has_year.group(1);
            elif has_year.group(2):
                year = has_year.group(2);
            elif has_year.group(3):
                year = has_year.group(3);
            else:
                year = UNKNOWN_YEAR;
            break;

    return int(year);

def remove_user_tags(file):
    return re_usertags.sub("",  file);

def remove_meta_tags(file):
    return re_metatags.sub("", file);

def remove_file_extension(file):
    file_name, extension = os.path.splitext(file);

    if extension in FILE_EXTENSIONS:
        file = file_name;

    return file;

def is_media(file):
    file_name, extension = os.path.splitext(file);
    return extension in MEDIA_EXTENSIONS;

def is_subtitle(file):
    file_name, extension = os.path.splitext(file);
    return extension in SUB_TITLE_EXTENSIONS;

def is_oad(file):
    return re_oad.search(remove_user_tags(remove_meta_tags(file))) != None;

def is_extra(file):
    return re_extra.search(remove_user_tags(remove_meta_tags(file))) != None;

def is_ncop(file):
    return re_ncop.search(remove_user_tags(remove_meta_tags(file))) != None;

def is_nced(file):
    return re_nced.search(remove_user_tags(remove_meta_tags(file))) != None;
