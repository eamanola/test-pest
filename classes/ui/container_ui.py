from classes.container import Season, Show, Extra
from classes.ui.media_ui import MediaUI
from classes.identifiable import Identifiable
from classes.ext_apis.anidb import AniDB


class ContainerUI(object):

    def __init__(self, container):
        super(ContainerUI, self).__init__()
        self._container = container

    def container(self):
        return self._container

    @staticmethod
    def html_page(container, meta=None):
        page = ContainerUI.html_line(container, True)

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

        if is_title:
            title = f'<span class="title">{container.title()}</span>'
        else:
            title = f'''
                <span class="title js-navigation">{container.title()}</span>
                '''.strip()

        description_str = ""
        if (
            is_title and
            isinstance(container, Identifiable) and
            container.meta() and
            container.meta().description()
        ):
            description_str = f'''
                <span class="description">
                    {container.meta().description()}
                </span>'''.strip()

        rating_str = ""
        if (
            isinstance(container, Identifiable) and
            container.meta() and
            container.meta().rating()
        ):
            rating_str = f'''
                <span class="rating">
                    {container.meta().rating()} / 10
                </span>'''.strip()

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

        # add_to_play = '<a href="#" class="js-add-to-play">+Play</a>'
        # played = '<a href="#" class="js-played">Played</a>'
        add_to_play = ''
        played = ''

        actions = f'''
            <span class="actions">
                {anidb}
                {add_to_play}
                {played}
                {scan}
                {identify}
            </span>
        '''.strip()

        return f'''
            <div class="container
                {"line" if not is_title else ""}
                js-container" data-id="{container.id()}">
                <img
                    src="{
                    "/images/posters/" + container.poster()
                    if container.poster() else ""
                    }"
                    class="poster" />
                {description_str}
                <div class="middle">
                    {parent_str}
                    {title}
                    <br />
                    {rating_str}
                </div>
                <span class="right">
                    {actions}
                </span>
            </div>
        '''.strip()
