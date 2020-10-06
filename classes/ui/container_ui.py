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
    def html_page(container):
        page = ContainerUI.html_line(container, True)

        for con in sorted(container.containers, key=lambda c: c.title()):
            page = f"""
                {page}
                {ContainerUI.html_line(con)}
                """

        for med in sorted(container.media, key=lambda m: m.title()):
            page = f"""
                    {page}
                    {MediaUI.html_line(med)}
                    """

        return page

    @staticmethod
    def html_line(container, is_title=False):

        if is_title:
            title = f'<span>{container.title()}</span>'
        else:
            title = f'<span class="js-navigation">{container.title()}</span>'

        if (
            container.parent() and
            (
                is_title or
                isinstance(container.parent(), (Season, Extra))
            )
        ):
            parent = f'''
                <span
                    class="js-navigation js-container"
                    data-id="{container.parent().id()}"
                >
                    {container.parent().title()}
                </span> &nbsp;
            '''
        else:
            parent = ""

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
                aniDB
            </a>&nbsp;
            '''
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
                {add_to_play}
                {played}
                {scan}
                {identify}
            </span>
        '''

        return f'''
            <div class="container js-container" data-id="{container.id()}">
                <img src="{container.thumbnail()}" />
                {parent}
                {title}
                <span class="right">
                    {anidb}
                    {actions}
                </span>
            </div>
        '''
