import os
from classes.file_name_parser import File_name_parser
from classes.container import MediaLibrary, Show, Season, Extra
from classes.media import Episode, Movie


class Scanner(object):

    def __init__(self):
        super(Scanner, self).__init__()

    @staticmethod
    def scan(file_paths, root_container):
        for file_path in file_paths:
            current_container = root_container

            show_name = File_name_parser.guess_show_name(file_path)
            year = File_name_parser.guess_year(file_path)
            season_number = File_name_parser.guess_season(file_path)
            episode_number = File_name_parser.guess_episode(file_path)
            is_media = File_name_parser.is_media(file_path)
            is_subtitle = File_name_parser.is_subtitle(file_path)
            is_extra = File_name_parser.is_extra(file_path)
            is_oad = File_name_parser.is_oad(file_path)
            is_ncop = File_name_parser.is_ncop(file_path)
            is_nced = File_name_parser.is_nced(file_path)
            is_ova = File_name_parser.is_ova(file_path)

            is_show = (
                season_number or
                episode_number or
                is_extra
            )
            is_movie = not is_show

            if not year:
                year = None

            if is_show:
                show = Show(
                    root_container.path(),
                    show_name,
                    parent=current_container
                )

                existing = current_container.get_container(show.id())
                if existing:
                    show = existing
                else:
                    current_container.containers.append(show)

                current_container = show
                show.set_year(year)

                # identify(db, show, show_name, year, Ext_api.TV_SHOW)

                if season_number:
                    season = Season(
                        root_container.path(),
                        show_name,
                        season_number,
                        parent=current_container
                    )
                    existing = current_container.get_container(season.id())
                    if existing:
                        season = existing
                    else:
                        current_container.containers.append(season)

                    current_container = season

                if is_extra:
                    extra = Extra(
                        root_container.path(),
                        show_name,
                        season_number,
                        parent=current_container
                    )
                    existing = current_container.get_container(extra.id())
                    if existing:
                        extra = existing
                    else:
                        current_container.containers.append(extra)

                    current_container = extra

                if episode_number or is_extra:
                    media = Episode(
                        file_path,
                        episode_number,
                        False,
                        parent=current_container,
                        is_oad=is_oad,
                        is_ncop=is_ncop,
                        is_nced=is_nced,
                        is_ova=is_ova
                    )
                    existing = current_container.get_media(media.id())
                    if existing:
                        media = existing
                    else:
                        current_container.media.append(media)

            elif is_movie:
                media = Movie(
                    file_path,
                    show_name,
                    False,
                    parent=current_container
                )
                existing = current_container.get_media(media.id())
                if existing:
                    media = existing
                else:
                    current_container.media.append(media)
                # identify(db, media, show_name, year, Ext_api.MOVIE)
                media.set_year(year)

            if media:
                if is_media:
                    media.file = file_path

                elif is_subtitle:
                    media.subtitles.append(file_path)

        return root_container

    @staticmethod
    def ls_path(base_path):
        file_paths = []
        for dirpath, dirnames, filenames in os.walk(
            base_path,
            followlinks=True
        ):
            for filename in filenames:
                filename = os.path.join(dirpath, filename).replace(
                    base_path, ""
                )
                file_paths.append(filename)

        return file_paths

    @staticmethod
    def filter_types(file_paths):
        types = File_name_parser.FILE_EXTENSIONS
        return [
            filename for filename in file_paths if filename.endswith(types)
        ]

    @staticmethod
    def filter_media_library(media_library):
        file_paths = Scanner.ls_path(media_library.path())

        file_paths = Scanner.filter_types(file_paths)

        return file_paths

    @staticmethod
    def filter_show(show):
        file_paths = Scanner.filter_media_library(show)

        if show.show_name():
            show_paths = []
            for file_path in file_paths:
                if (
                    File_name_parser.guess_show_name(file_path) ==
                    show.show_name()
                ):
                    show_paths.append(file_path)

            file_paths = show_paths

        return file_paths

    @staticmethod
    def filter_season(season):
        file_paths = Scanner.filter_show(season)

        if season.season_number():
            season_paths = []
            for file_path in file_paths:
                if (
                    File_name_parser.guess_season(file_path) ==
                    season.season_number()
                ):
                    season_paths.append(file_path)

            file_paths = season_paths

        return file_paths

    @staticmethod
    def filter_extra(extra):
        file_paths = Scanner.filter_season(extra)

        extra_paths = []

        for file_path in file_paths:
            if File_name_parser.is_extra(file_path):
                extra_paths.append(file_path)

            file_paths = extra_paths

        return file_paths

    @staticmethod
    def scan_media_library(media_library):
        file_paths = Scanner.filter_media_library(media_library)

        result = Scanner.scan(file_paths, media_library)

        Scanner._remove_singles(result)

        return result

    @staticmethod
    def scan_show(show):
        file_paths = Scanner.filter_show(show)

        media_library = MediaLibrary(show.path())
        Scanner.scan(file_paths, media_library)

        result = media_library.find_container(show.id())

        Scanner._remove_singles(result)

        return result

    @staticmethod
    def scan_season(season):
        file_paths = Scanner.filter_season(season)

        media_library = MediaLibrary(season.path())
        Scanner.scan(file_paths, media_library)

        result = media_library.find_container(season.id())

        Scanner._remove_singles(result)

        return result

    @staticmethod
    def scan_extra(extra):
        file_paths = Scanner.filter_extra(extra)

        media_library = MediaLibrary(extra.path())
        Scanner.scan(file_paths, media_library)

        result = media_library.find_container(extra.id())

        Scanner._remove_singles(result)

        return result

    @staticmethod
    def _remove_singles(container):
        if isinstance(container, (Extra, Season, Show)):
            if len(container.containers) == 1 and len(container.media) == 0:
                remove = container.containers[0]

                for con in remove.containers:
                    con._parent = container
                    container.containers.append(con)

                for med in remove.media:
                    med._parent = container
                    container.media.append(med)

                remove.containers.clear()
                remove.media.clear()

                container.containers.remove(remove)

                Scanner._remove_singles(container)

        for con in container.containers:
            Scanner._remove_singles(con)
