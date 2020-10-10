from classes.container import Show, Season, Extra
from classes.identifiable import Identifiable
from classes.ext_apis.anidb import AniDB
from classes.media import Movie
from classes.images import Images


class MediaUI(object):

    def __init__(self):
        super(MediaUI, self).__init__()

    @staticmethod
    def html_page(media):
        page = MediaUI.html_line(media, True)

        return page

    @staticmethod
    def html_line(
        media,
        is_title=False,
        parent=None,
        title=None,
        summary=None
    ):

        img_str = ""
        if isinstance(media, Identifiable):
            poster = Images.poster(media)
            if poster:
                img_str = f'<img class="poster" src="{poster}" />'

        if not img_str:
            thumbnail = Images.thumbnail(media, create_ifmissing=True)
            img_str = f'<img class="thumbnail" src="{thumbnail}" />'

        summary_str = ""
        if summary and is_title:
            summary_str = f'''
                <span class="summary">
                    {summary}
                </span>'''.strip()

        parent = media.parent() if parent is None else parent
        parents = []
        while(parent and isinstance(parent, (Show, Season, Extra))):
            parents.append(
                f'''
                <span
                    class="js-navigation js-parent parent"
                    data-id="{parent.id()}"
                >
                    {parent.title()}</span>&nbsp;
                <span class="parent">/</span>&nbsp;
                '''
            )
            parent = parent.parent()

        parents.reverse()
        parent_str = ''.join(parents)
        parent_str = f'''
        <span class="js-parents"
            {'style="display:none"' if not is_title else ""}>
            {parent_str}
        </span>
        '''

        if not title:
            if isinstance(media, Identifiable) and media.meta():
                title = media.meta().title()

        if not title:
            title = media.title()

        if is_title:
            title_str = f'<span class="title">{title}</span>'
        else:
            title_str = f'<span class="title js-navigation">{title}</span>'

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
            '''
        else:
            anidb = ""

        scan = ''

        identify = ''
        if media.__class__.__name__ == "Movie":
            identify = '<a href="#" class="js-identify">Identify</a>'

        add_to_play = '<a href="#" class="js-add-to-play">+Play</a>'
        played = f'''
            <label>
                Played
                <input
                    type="checkbox"
                    class="js-played"
                    {'checked="checked"' if media.played() else ''}
                    ></input>
            </label>
            '''

        actions = f'''
            <span class="actions">
                {anidb}
                {add_to_play}
                {played}
                {scan}
                {identify}
            </span>
        '''

        return f'''
            <div class="media js-media {
            "line" if not is_title else ""
            }" data-id="{media.id()}">
                {img_str}
                {summary_str}
                <div class="middle">
                    {parent_str}
                    {title_str}
                </div>
                <span class="right">
                    {actions}
                </span>
            </div>
        '''
