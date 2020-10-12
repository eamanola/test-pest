from classes.container import Show, Season, Extra
from classes.identifiable import Identifiable
from classes.ext_apis.anidb import AniDB
from classes.media import Movie, Episode
from classes.images import Images


class MediaUI(object):

    def __init__(self):
        super(MediaUI, self).__init__()

    @staticmethod
    def html_page(media):

        parents_strs = []
        parent = media.parent()
        while parent and isinstance(parent, (Extra, Season, Show)):
            parents_strs.append(
                f'''
                <span class="js-navigation js-parent" data-id="{parent.id()}">{
                    parent.title()
                }</span>
                '''.strip()
            )
            parent = parent.parent()
        parents_strs.reverse()
        print(parents_strs)
        parents_str = ' / '.join(parents_strs)
        parents_str = f'<span class="parents">[{parents_str}]</span>'

        img_str = ""
        img_src = None
        if isinstance(media, Identifiable):
            img_src = Images.poster(media)

        if not img_src:
            img_src = Images.thumbnail(media, create_ifmissing=True)

        if img_src:
            img_str = f'<img src="{img_src}" class="poster" />'

        episode_meta = None
        if isinstance(media, Episode) and media.episode_number():
            parent = media.parent()
            while(parent and not parent.meta()):
                parent = parent.parent()
            if (
                parent and
                isinstance(parent, Identifiable) and
                parent.meta() and
                parent.meta().episodes()
            ):
                for episode in parent.meta().episodes():
                    if episode[0] == media.episode_number():
                        episode_meta = episode
                        break

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
    def html_line(media):
        # img
        img_str = ""
        img_src = None
        img_class = None
        if isinstance(media, Identifiable):
            img_src = Images.poster(media)
            img_class = "poster"

        if not img_src:
            img_src = Images.thumbnail(media, create_ifmissing=True)
            img_class = "thumbnail"

        if img_src:
            img_str = f'<img src="{img_src}" class="js-play {img_class}" />'

        # parents
        parent = media.parent()

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

        episode_meta = None
        if isinstance(media, Episode) and media.episode_number():
            parent = media.parent()
            while parent and not parent.meta():
                parent = parent.parent()

            if (
                parent and
                isinstance(parent, Identifiable) and
                parent.meta() and
                parent.meta().episodes()
            ):
                for episode in parent.meta().episodes():
                    if episode[0] == media.episode_number():
                        episode_meta = episode
                        break

        # title
        title = None
        if episode_meta:
            title = f'{episode_meta[0]}. {episode_meta[1]}'

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
                        <span class="line2" class="right">
                            {add_to_play_str}
                            {played_str}
                            {identify_str}
                        </span>
                    </span>
                </span>
                <span class="right">
                    <span class="line1">
                        {anidb}
                    <!-- {add_to_play_str} -->
                    </span>
                    <span class="line2">
                        <!-- {played_str} -->
                        <!-- {identify_str} -->
                    </span>
                </span>
            </div>
        '''.strip()
