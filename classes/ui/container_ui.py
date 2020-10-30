from classes.ui.html_ui import HTMLUI

# deprecated


class ContainerUI(object):

    def __init__(self):
        super(ContainerUI, self).__init__()

    def _img_str(container):
        from classes.identifiable import Identifiable
        from classes.images import Images
        img_str = None

        if isinstance(container, Identifiable):
            poster = Images.poster(container)
            if poster:
                img_str = f'<img src="{poster}" class="poster" />'

        return img_str if img_str else ""

    _scan_str = '<a href="#" class="js-scan">Scan</a>'

    def _unplayed_str(container):
        unplayed_str = None

        if (container.unplayed_count() > 0):
            unplayed_str = ''.join([
                '<span class="unplayed">',
                f'[{container.unplayed_count()}]',
                '</span>'
            ])

        return unplayed_str if unplayed_str else ""

    @staticmethod
    def html_page(container):
        from classes.ui.media_ui import MediaUI
        page = ''.join([line.lstrip() for line in [
            f'''<div class="container js-container page header"
                data-id="{container.id()}">''',
            f'  {ContainerUI._img_str(container)}',
            '   <span class="info">',
            f'    {HTMLUI.title_html(container, navigation=False)}',
            f'    {HTMLUI.parents_html(container)}',
            f'    {HTMLUI.description_html(container)}',
            f'    {ContainerUI._scan_str}',
            f'    {HTMLUI.identify_html(container, show_ifneeded=False)}',
            f'    {HTMLUI.anidb_html(container)}',
            f'    {HTMLUI.get_info_html(container, show_ifneeded=False)}',
            '   </span>',
            '</div>\n'
        ]])

        for con in sorted(
            container.containers,
            key=lambda c: (
                c.unplayed_count() == 0,
                c.unplayed_count(),
                c.title()
            )
        ):
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
            '<div class="container line js-container" ',
            f'data-id="{container.id()}">',
            '<span class="left">',
            f'      {ContainerUI._img_str(container)}',
            '      <span class="info">',
            '          <span class="line1">',
            f'              {HTMLUI.parents_html(container)}',
            f'              {HTMLUI.title_html(container, navigation=True)}',
            '          </span>',
            '          <span class="line2">',
            f'              {HTMLUI.rating_html(container)}',
            f'              {ContainerUI._unplayed_str(container)}',
            f'''            {HTMLUI.played_html(
                                container,
                                container.unplayed_count() == 0
                            )}''',
            '          </span>',
            '      </span>',
            '  </span>',
            '  <span class="right">',
            '      <span class="line1">',
            f'          {HTMLUI.get_info_html(container)}',
            f'          {ContainerUI._scan_str}',
            f'          {HTMLUI.identify_html(container)}'
            '      </span>',
            '  </span>',
            '</div>\n'
        ])
