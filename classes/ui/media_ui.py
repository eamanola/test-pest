from classes.container import Show, Season, Extra
from classes.identifiable import Identifiable
from classes.ext_apis.anidb import AniDB
from classes.media import Movie
from classes.images import Images


class MediaUI(object):

    def __init__(self):
        super(MediaUI, self).__init__()

    @staticmethod
    def html_page(media, parents, episode_meta=None):

        print(parents)

        parents_strs = []
        for parent in parents:
            parents_strs.append(
                f'''
                <span class="js-navigation js-parent" data-id="{parent.id()}">{
                    parent.title()
                }</span>
                '''.strip()
            )
        parents_strs.reverse()
        print(parents_strs)
        parents_str = ' / '.join(parents_strs)
        parents_str = f'<span class="parents">[{parents_str}]</span>'

        img_str = ""
        if isinstance(media, Identifiable):
            poster = Images.poster(media)
            if poster:
                img_str = f'<img src="{poster}" class="poster" />'

        if not img_str:
            thumbnail = Images.thumbnail(media, create_ifmissing=True)
            img_str = f'<img src="{thumbnail}" class="poster" />'

        title_str = ""
        title = None
        if isinstance(media, Identifiable):
            if media.meta() and media.meta().title():
                title = media.meta().title()
        if not title:
            if episode_meta:
                title = f'{episode_meta[0]}. {episode_meta[1]}'

        if not title:
            title = media.title()

        title_str = f'<span class="title">{title}</span>'

        description = None
        description_str = ""
        if (
            isinstance(media, Identifiable) and
            media.meta() and
            media.meta().description()
        ):
            description = media.meta().description()

        if not description and episode_meta:
            description = episode_meta[2]

        if description:
            description_str = f'''
                <span class="description">
                    {description}
                </span>'''.strip()

        page = f'''
        <div class="media page header" data-id="{media.id()}">
            {img_str}
            <span class="info">
                {title_str}
                {parents_str}
                {description_str}
                <span style="display:none">
                </span>
            </span>
        </div>
        '''.strip()

        return page

    @staticmethod
    def html_line(
        media,
        parent=None,
        title=None
    ):
        # img
        img_str = ""
        if isinstance(media, Identifiable):
            poster = Images.poster(media)
            if poster:
                img_str = f'<img class="poster" src="{poster}" />'

        if not img_str:
            thumbnail = Images.thumbnail(media, create_ifmissing=True)
            img_str = f'<img class="thumbnail" src="{thumbnail}" />'

        # parents
        parent = parent if parent else media.parent()

        parents = []
        while(parent and isinstance(parent, (Show, Season, Extra))):
            parents.append(
                f'''
            <span class="js-navigation js-parent" data-id="{parent.id()}">{
                parent.title()
            }</span>'''.strip()
            )
            parent = parent.parent()
        parents.reverse()

        parents_str = '/'.join(parents)
        parents_str = f'''
        <span class="js-parents" style="display:none">{parents_str}</span>
        '''.strip()

        # title
        if not title:
            if isinstance(media, Identifiable) and media.meta():
                title = media.meta().title()

        if not title:
            title = media.title()

        class_str = "js-navigation" if (
            isinstance(media, Movie) or
            (
                not media.is_oad() and
                not media.is_ncop() and
                not media.is_nced()
            )
        ) else ""
        title_str = f'<span class="{class_str}">{title}</span>'

        # anidb
        if (
            isinstance(media, Identifiable) and
            AniDB.KEY in media.ext_ids()
        ):
            anidb = f'''
            <a
                href="https://anidb.net/anime/{media.ext_ids()[AniDB.KEY]}"
                target="_blank"
                rel="noopener noreferrer"
                class="extrenal-link">
                aniDB</a>
            <a href="#" class="js-get-info">Get Info</a>&nbsp;
            '''.strip()
        else:
            anidb = ""

        add_to_play_str = '<a href="#" class="js-add-to-play">+Play</a>'

        played_str = f'''
            <label>
                Played
                <input
                    type="checkbox"
                    class="js-played"
                    {'checked="checked"' if media.played() else ''}
                    ></input>
            </label>
            '''.strip()

        identify_str = ""
        if isinstance(media, Identifiable):
            identify_str = '<a href="#" class="js-identify">Identify</a>'

        return f'''
            <div class="media js-media line" data-id="{media.id()}">
                <span class="left">
                    {img_str}
                    <span class="info">
                        <span class="line1">
                            {parents_str}
                            {title_str}
                        </span>
                        <span class="line2" style="display:none">
                        </span>
                    </span>
                </span>
                <span class="right">
                    <span class="line1">
                        {anidb}
                        {add_to_play_str}
                    </span>
                    <span class="line2">
                        {played_str}
                        {identify_str}
                    </span>
                </span>
            </div>
        '''.strip()
