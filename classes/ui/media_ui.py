from classes.container import Show, Season, Extra
from classes.identifiable import Identifiable
from classes.ext_apis.anidb import AniDB


class MediaUI(object):

    def __init__(self):
        super(MediaUI, self).__init__()

    @staticmethod
    def html_page(media):
        page = MediaUI.html_line(media, True)

        return page

    @staticmethod
    def html_line(media, is_title=False):
        if is_title:
            title = f'<span>{media.title()}</span>'
        else:
            title = f'<span class="js-navigation">{media.title()}</span>'

        if is_title and media.parent() and isinstance(
            media.parent(), (Show, Season, Extra)
        ):
            parent = f'''
            <span
                class="js-navigation js-container"
                data-id="{media.parent().id()}"
            >
                {media.parent().title()}
            </span> &nbsp;
            '''
        else:
            parent = ""

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
                aniDB
            </a>&nbsp;
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
                {add_to_play}
                {played}
                {scan}
                {identify}
            </span>
        '''

        return f'''
            <div class="media js-media" data-id="{media.id()}">
                <img src="{media.thumbnail()}" />
                {parent}
                {title}
                <span class="right">
                    {anidb}
                    {actions}
                </span>
            </div>
        '''
