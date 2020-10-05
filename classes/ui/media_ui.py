from classes.container import Show, Season, Extra


class MediaUI(object):

    def __init__(self):
        super(MediaUI, self).__init__()

    @staticmethod
    def html_line(media, is_title=False):

        if is_title and media.parent() and isinstance(
            media.parent(), (Show, Season, Extra)
        ):
            parent = f'''
            <span
                class="js-navigation
                js-container"
                data-id="{media.parent().id()}"
            >
                {media.parent().title()}
            </span> &nbsp;
            '''
        else:
            parent = ""
        return f'''
            <div class="media js-media" data-id="{media.id()}">
                <img src="{media.thumbnail()}" />
                {parent}
                <span class="js-navigation">{media.title()}</span>
            </div>
        '''
