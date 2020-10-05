from classes.container import Show, Season, Extra


class MediaUI(object):

    def __init__(self):
        super(MediaUI, self).__init__()

    @staticmethod
    def html_line(media, is_title=False):
        include_parent = (
            is_title and
            media.parent() and
            isinstance(media.parent(), (Show, Season, Extra))
        )

        return f'''
            <div class="media">
                <img src="{media.thumbnail()}" />
                {{parent}}
                <span
                    class="js-media"
                    data-id="{media.id()}"
                >
                    {media.title()}
                </span>
            </div>
        '''.format(parent=f'''
            <span class="parent js-parent" data-id="{media.parent().id()}">
                {media.parent().title()}
            </span> &nbsp;
            ''' if include_parent else "")
