from classes.container import Season, Show, Extra
from classes.ui.media_ui import MediaUI


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
            title = f'''
                <span
                    class="js-container"
                    data-id="{container.id()}"
                >
                    {container.title()}
                </span>
            '''

        if (
            container.parent() and
            (
                is_title or
                isinstance(container.parent(), (Season, Extra))
            )
        ):
            parent = f'''
                <span
                    class="parent js-parent"
                    data-id="{container.parent().id()}"
                >
                    {container.parent().title()}
                </span> &nbsp;
            '''
        else:
            parent = ""

        return f'''
            <div class="container">
                <img src="{container.thumbnail()}" />
                {parent}
                {title}
            </div>
        '''
