from classes.identifiable import Identifiable
from classes.container import Container, Extra, Season, Show
from classes.media import Episode


class HTMLUI(object):

    def __init__(self):
        super(HTML_UI, self).__init__()

    def anidb_html(identifiable):
        from classes.ext_apis.anidb import AniDB
        anidb_str = None

        if (
            isinstance(identifiable, Identifiable) and
            AniDB.KEY in identifiable.ext_ids()
        ):
            anidb_str = [
                '<a href="'
                f'https://anidb.net/anime/{identifiable.ext_ids()[AniDB.KEY]}'
                '" target="_blank" rel="noopener noreferrer" ',
                'class="external-link js-external-link">',
                'aniDB',
                '</a>'
            ]
            anidb_str = ''.join(anidb_str)

        return anidb_str if anidb_str else ""

    def get_info_html(identifiable, show_ifneeded=True):
        show_get_info = (
            isinstance(identifiable, Identifiable) and
            len(identifiable.ext_ids()) > 0 and
            (
                not show_ifneeded or
                not identifiable.meta()
            )
        )

        if show_get_info:
            text = "Get Info" if not identifiable.meta() else "Update Info"
            html = f'<a href="#" class="js-get-info">{text}</a>'
        else:
            html = ""

        return html

    def rating_html(identifiable):
        if (
            isinstance(identifiable, Identifiable) and
            identifiable.meta() and
            identifiable.meta().rating()
        ):
            html = ''.join([
                '<span class="rating">',
                f'{identifiable.meta().rating()} / 10',
                '</span>'
            ])
        else:
            html = ""

        return html

    def identify_html(identifiable, show_ifneeded=True):
        show_identify = (
            isinstance(identifiable, Identifiable) and
            (
                not isinstance(identifiable, Container) or
                identifiable.__class__.__name__ == "Show"
            ) and
            (not show_ifneeded or len(identifiable.ext_ids()) == 0)
        )

        if show_identify:
            html = '<a href="#" class="js-identify">Identify</a>'
        else:
            html = ""

        return html

    def description_html(item, episode_meta=None):
        description = None
        if (
            isinstance(item, Identifiable) and
            item.meta() and
            item.meta().description()
        ):
            description = item.meta().description()

        if not description and episode_meta:
            description = episode_meta.summary()

        if description:
            html = f'<span class="description">{description}</span>'
        else:
            html = ""

        return html

    def parents_html(item, display_none=False):
        parents = []
        parent = item.parent()
        while parent and isinstance(parent, (Extra, Season, Show)):
            parents.append(parent)
            parent = parent.parent()

        if len(parents):
            parents.reverse()

            parents_str = ' / '.join([
                ''.join([
                    '<span class="js-navigation js-parent" '
                    f'data-id="{parent.id()}">',
                    parent.title(),
                    '</span>'
                ]) for parent in parents
            ])

            wrapper_class_str = "parents"
            wrapper_style = ""
            if display_none:
                wrapper_class_str = f'{wrapper_class_str} js-parents'
                wrapper_style = " style=display:none"

            parents_str = ''.join([
                f'<span class="{wrapper_class_str}"{wrapper_style}>',
                f'[{parents_str}]',
                '</span>'
            ])

        return parents_str if len(parents) else ""

    def title_html(item, episode_meta=None, navigation=True):
        title = None
        if isinstance(item, Episode):
            if item.is_extra():
                title = item.title()
            elif episode_meta is not None:
                title = '. '.join([
                    str(episode_meta.episode_number()),
                    episode_meta.title()
                ])

            navigation = navigation and not item.is_extra()

        if not title and isinstance(item, Identifiable) and item.meta():
            title = item.meta().title()

        if not title:
            title = item.title()

        class_str = ' class="js-navigation"' if navigation else ""

        return f'<span{class_str}>{title}</span>'
