from classes.container import Show, Season, Extra
from classes.identifiable import Identifiable
from classes.media import Movie, Episode


class MediaUI(object):

    def __init__(self):
        super(MediaUI, self).__init__()

    def _img_str(media):
        from classes.images import Images
        img_src = None
        if isinstance(media, Identifiable):
            img_src = Images.poster(media)
            class_str = "poster"

        if not img_src:
            img_src = Images.thumbnail(media, create_ifmissing=True)
            class_str = "thumbnail"

        if img_src:
            img_str = ''.join([
                '<span class="js-play-wrapper">',
                f'<img src="{img_src}" class="js-play {class_str}" />',
                '</span>'
            ])

        return img_str if img_src else ""

    def _title_str(media, episode_meta, navigation=True):
        title = None
        if isinstance(media, Episode) and media.is_extra():
            title = media.title()

        if not title and episode_meta:
            title = '. '.join([
                str(episode_meta.episode_number()),
                episode_meta.title()
            ])

        if not title:
            if isinstance(media, Identifiable) and media.meta():
                title = media.meta().title()

        if not title:
            title = media.title()

        class_str = ' class="js-navigation"' if (
            navigation and (isinstance(media, Movie) or not media.is_extra())
        ) else ""

        title_str = f'<span{class_str}>{title}</span>'

        return title_str

    def _parents_str(media, display_none=False):
        parents_strs = []
        parent = media.parent()
        while parent and isinstance(parent, (Extra, Season, Show)):
            parents_strs.append(''.join([
                '<span class="js-navigation js-parent" '
                f'data-id="{parent.id()}">',
                parent.title(),
                '</span>'
            ]))
            parent = parent.parent()

        if len(parents_strs):
            parents_strs.reverse()

            parents_str = ' / '.join(parents_strs)

            class_str = "parents"
            style = ""
            if display_none:
                class_str = f'{class_str} js-parents'
                style = " style=display:none"

            parents_str = ''.join([
                f'<span class="{class_str}"{style}>',
                f'[{parents_str}]',
                '</span>'
            ])

        return parents_str if len(parents_strs) else ""

    def _description_str(media, episode_meta):
        description = None
        if (
            isinstance(media, Identifiable) and
            media.meta() and
            media.meta().description()
        ):
            description = media.meta().description()

        if not description and episode_meta:
            description = episode_meta.summary()

        if description:
            description_str = ''.join([
                '<span class="description">',
                description,
                '</span>'
            ])

        return description_str if description else ""

    def _anidb_str(media):
        from classes.ext_apis.anidb import AniDB
        anidb_str = None

        if (
            isinstance(media, Identifiable) and
            AniDB.KEY in media.ext_ids()
        ):
            anidb_str = ''.join([
                '<a href="'
                f'https://anidb.net/anime/{media.ext_ids()[AniDB.KEY]}'
                '" target="_blank" rel="noopener noreferrer" ',
                'class="external-link js-external-link">',
                'aniDB',
                '</a>',
                '<a href="#" class="js-get-info">Get Info</a>'
            ])

        return anidb_str if anidb_str else ""

    _add_to_play_str = '<a href="#" class="js-add-to-play">+Play</a>'

    def _played_str(media):
        return ''.join([
            '<label><input type="checkbox" class="js-played"',
            ' checked="checked"' if media.played() else '',
            '/><span>Played</span></label>'
        ])

    def _identify_str(media):
        identify_str = ""
        if isinstance(media, Identifiable):
            identify_str = '<a href="#" class="js-identify">Identify</a>'

        return identify_str

    @staticmethod
    def html_page(media):
        episode_meta = None
        if isinstance(media, Episode) and media.episode_number():
            parent = media.parent()
            while(
                parent and
                not (isinstance(parent, Identifiable) and parent.meta())
            ):
                parent = parent.parent()

            if (
                parent and
                isinstance(parent, Identifiable) and
                parent.meta()
            ):
                episode_meta = parent.meta().get_episode(media)

        page = ''.join([line.lstrip() for line in [
            f'<div class="media page header" data-id="{media.id()}">',
            f'  {MediaUI._img_str(media)}',
            f'  <span class="info">',
            f'''      {MediaUI._title_str(
                        media,
                        episode_meta,
                        navigation=False
                    )}''',
            f'      {MediaUI._parents_str(media)}',
            f'      {MediaUI._description_str(media, episode_meta)}',
            '   </span>',
            '</div>'
        ]])

        return page

    @staticmethod
    def html_line(media):
        episode_meta = None
        if isinstance(media, Episode) and media.episode_number():
            parent = media.parent()
            while (
                parent and
                not (isinstance(parent, Identifiable) and parent.meta())
            ):
                parent = parent.parent()

            if (
                parent and
                isinstance(parent, Identifiable) and
                parent.meta()
            ):
                episode_meta = parent.meta().get_episode(media)

        return ''.join(line.lstrip() for line in [
            f'<div class="media js-media line" data-id="{media.id()}">',
            '   <span class="left">',
            f'      {MediaUI._img_str(media)}',
            '       <span class="info">',
            '           <span class="line1">',
            f'              {MediaUI._parents_str(media, display_none=True)}',
            f'              {MediaUI._title_str(media, episode_meta)}',
            '           </span>',
            '           <span class="line2">',
            f'              {MediaUI._add_to_play_str}',
            f'              {MediaUI._played_str(media)}',
            '           </span>',
            '       </span>',
            '   </span>',
            '   <span class="right">',
            '       <span class="line1">',
            f'          {MediaUI._anidb_str(media)}',
            '       </span>',
            f'      <span class="line2">',
            f'          {MediaUI._identify_str(media)}',
            '       </span>',
            '   </span>',
            '</div>\n'
        ])
