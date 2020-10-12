from classes.container import Show, Season, Extra
from classes.identifiable import Identifiable


class ContainerUI(object):

    def __init__(self):
        super(ContainerUI, self).__init__()

    def _img_str(container):
        from classes.images import Images
        img_str = None

        if isinstance(container, Identifiable):
            poster = Images.poster(container)
            if poster:
                img_str = f'<img src="{poster}" class="poster" />'

        return img_str if img_str else ""

    def _title_str(container, include_parents=False):
        parents_str = ""

        if include_parents:
            parent_title_strs = []
            parent = container.parent()
            while parent and parent.__class__.__name__ != "MediaLibrary":
                parent_title_strs.append(parent.title())
                parent = parent.parent()

            if len(parent_title_strs):
                parents_str = f'[{"/".join(parent_title_strs)}] '

        return f'<span class="title">{parents_str}{container.title()}</span>'

    def _description_str(container):
        description_str = None

        if (
            isinstance(container, Identifiable) and
            container.meta() and
            container.meta().description()
        ):
            description_str = ''.join([
                '<span class="description">',
                container.meta().description(),
                '</span>'
            ])

        return description_str if description_str else ""

    _scan_str = '<a href="#" class="js-scan">Scan</a>'

    def _parent_str(container):
        parent_str = None

        if (container.parent() and (
            isinstance(container.parent(), (Show, Season, Extra))
        )):
            parent_str = ''.join([
                '<span class="parent js-navigation js-container" ',
                f'data-id="{container.parent().id()}">',
                container.parent().title(),
                '</span>'
            ])

        return parent_str if parent_str else ""

    def _rating_str(container):
        rating_str = None
        if (
            isinstance(container, Identifiable) and
            container.meta() and
            container.meta().rating()
        ):
            rating_str = ''.join([
                '<span class="rating">',
                f'{container.meta().rating()} / 10',
                '</span>'
            ])

        return rating_str if rating_str else ""

    def _unplayed_str(container):
        unplayed_str = None

        if (container.unplayed_count() > 0):
            unplayed_str = ''.join([
                '<span class="unplayed">',
                f'[{container.unplayed_count()}]',
                '</span>'
            ])

        return unplayed_str if unplayed_str else ""

    def _anidb_str(container, show_ifneeded=True):
        from classes.ext_apis.anidb import AniDB
        anidb_str = None

        if (
            isinstance(container, Identifiable) and
            AniDB.KEY in container.ext_ids()
        ):
            anidb_str = [
                '<a href="'
                f'https://anidb.net/anime/{container.ext_ids()[AniDB.KEY]}'
                '" target="_blank" rel="noopener noreferrer" ',
                'class="external-link js-external-link">',
                'aniDB',
                '</a>'
            ]

            if not show_ifneeded or not container.meta():
                anidb_str.append(
                    '<a href="#" class="js-get-info">Get Info</a>'
                )
            anidb_str = ''.join(anidb_str)

        return anidb_str if anidb_str else ""

    def _identify_str(container, show_ifneeded=True):
        identify_str = None

        show_identify = not show_ifneeded or (
            isinstance(container, Identifiable) and
            len(container.ext_ids()) == 0
        )

        if show_identify and container.__class__.__name__ == "Show":
            identify_str = '<a href="#" class="js-identify">Identify</a>'

        return identify_str if identify_str else ""

    @staticmethod
    def html_page(container):
        from classes.ui.media_ui import MediaUI
        page = ''.join([line.lstrip() for line in [
            f'<div class="container page header" data-id="{container.id()}">',
            f'  {ContainerUI._img_str(container)}',
            '   <span class="info">',
            f'    {ContainerUI._title_str(container, include_parents=True)}',
            f'    {ContainerUI._description_str(container)}',
            f'    {ContainerUI._scan_str}',
            f'    {ContainerUI._identify_str(container, show_ifneeded=False)}',
            f'    {ContainerUI._anidb_str(container, show_ifneeded=False)}'
            '   </span>',
            '</div>\n'
        ]])

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
    def html_line(container, is_title=False, parent=None, meta=None):
        return ''.join(line.lstrip() for line in [
            '<div class="container line js-navigation js-container" ',
            f'data-id="{container.id()}">',
            '<span class="left">',
            f'      {ContainerUI._img_str(container)}',
            '      <span class="info">',
            '          <span class="line1">',
            f'              {ContainerUI._parent_str(container)}',
            f'              {ContainerUI._title_str(container)}',
            '          </span>',
            '          <span class="line2">',
            f'              {ContainerUI._rating_str(container)}',
            f'              {ContainerUI._unplayed_str(container)}',
            '          </span>',
            '      </span>',
            '  </span>',
            '  <span class="right">',
            '      <span class="line1">',
            f'          {ContainerUI._anidb_str(container)}',
            f'          {ContainerUI._scan_str}',
            f'          {ContainerUI._identify_str(container)}'
            '      </span>',
            '  </span>',
            '</div>\n'
        ])
