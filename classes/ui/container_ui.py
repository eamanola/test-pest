from classes.container import Season, Show, Extra
from classes.ui.media_ui import MediaUI
from classes.identifiable import Identifiable
from classes.ext_apis.anidb import AniDB
from classes.images import Images


class ContainerUI(object):

    def __init__(self, container):
        super(ContainerUI, self).__init__()
        self._container = container

    def container(self):
        return self._container

    @staticmethod
    def html_page(container, meta=None):
        img_str = ""
        if isinstance(container, Identifiable):
            poster = Images.poster(container)
            if poster:
                img_str = f'<img src="{poster}" class="poster" />'

        title_str = f'<span class="title">{container.title()}</span>'

        description_str = ""
        if (
            isinstance(container, Identifiable) and
            container.meta() and
            container.meta().description()
        ):
            description_str = f'''
                <span class="description">
                    {container.meta().description()}
                </span>'''.strip()

        scan_str = '<a href="#" class="js-scan">Scan</a>'

        page = f'''
        <div class="container page header" data-id="{container.id()}">
            {img_str}
            <span class="info">
                {title_str}
                {description_str}
                <span>
                    {scan_str}
                </span>
            </span>
        </div>
        '''

        for con in sorted(container.containers, key=lambda c: c.title()):
            page = f"""
                {page}
                {ContainerUI.html_line(con)}
                """

        use_meta_titles = (
            meta is not None and
            not isinstance(container, Extra)
        )

        for med in sorted(container.media, key=lambda m: m.title()):
            title = None
            if use_meta_titles:
                meta_episode = [
                    m for m in meta.episodes()
                    if m[0] == med.episode_number()
                ]
                if len(meta_episode):
                    meta_episode = meta_episode[0]
                    title = f'{str(meta_episode[0])}. {meta_episode[1]}'

            page = f"""
                    {page}
                    {MediaUI.html_line(
                        med,
                        parent=container,
                        title=title
                    )}
                    """

        return page

    @staticmethod
    def html_line(container, is_title=False, parent=None, meta=None):

        img_str = ""
        if isinstance(container, Identifiable):
            poster = Images.poster(container)
            if poster:
                img_str = f'<img src="{poster}" class="poster" />'

        parent_str = ""
        if (container.parent() and (
            isinstance(container.parent(), (Show, Season, Extra))
        )):
            parent_str = f'''
                <span
                    class="parent js-navigation js-container"
                    data-id="{container.parent().id()}"
                >{container.parent().title()}</span> &nbsp;
            '''.strip()

        title_str = f'''
            <span class="title js-navigation">{container.title()}</span>
            '''.strip()

        rating_str = ""
        if (
            isinstance(container, Identifiable) and
            container.meta() and
            container.meta().rating()
        ):
            rating_str = f'''
                <span class="rating middle-line2">
                    {container.meta().rating()} / 10
                </span>&nbsp;'''.strip()

        unplayed_str = ""
        if (container.unplayed_count() > 0):
            unplayed_str = f'''
                <span class="unplayed middle-line2">
                    [{container.unplayed_count()}]
                </span>&nbsp;'''.strip()

        if (
            isinstance(container, Identifiable) and
            AniDB.KEY in container.ext_ids()
        ):
            anidb = f'''
            <a
                href="https://anidb.net/anime/{container.ext_ids()[AniDB.KEY]}"
                target="_blank"
                rel="noopener noreferrer"
                class="extrenal-link">
                aniDB</a>
            <a href="#" class="js-get-info">Get Info</a>&nbsp;
            '''.strip()
        else:
            anidb = ""

        scan = '<a href="#" class="js-scan">Scan</a>'

        identify = ''
        if container.__class__.__name__ == "Show":
            identify = '<a href="#" class="js-identify">Identify</a>'

        return f'''
            <div class="container line js-container" data-id="{
                container.id()
            }">
                <span class="left">
                    {img_str}
                    <span class="info">
                        <span class="line1">
                            {parent_str}
                            {title_str}
                        </span>
                        <span class="line2">
                            {rating_str}
                            {unplayed_str}
                        </span>
                    </span>
                </span>
                <span class="right">
                    <span class="line1">
                        {anidb}
                    </span>
                    <span class="line2">
                        {scan}
                        {identify}
                    </span>
                </span>
            </div>
        '''.strip()
