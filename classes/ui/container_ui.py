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

    def _title_str(container):
        return f'<span class="title">{container.title()}</span>'

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

        return description_str

    _scan_str = '<a href="#" class="js-scan">Scan</a>'

    def _parent_str(container):
        parent_str = None

        if (container.parent() and (
            isinstance(container.parent(), (Show, Season, Extra))
        )):
            parent_str = ''.join([
                '<span class="parent js-navigation js-container" ',
                f'data-id="{container.parent().id()}">',
                {container.parent().title()},
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

    def _anidb_str(container):
        from classes.ext_apis.anidb import AniDB
        anidb_str = None

        if (
            isinstance(container, Identifiable) and
            AniDB.KEY in container.ext_ids()
        ):
            anidb_str = ''.join([
                '<a href="'
                f'https://anidb.net/anime/{container.ext_ids()[AniDB.KEY]}'
                '" target="_blank" rel="noopener noreferrer" ',
                'class="external-link js-external-link">',
                'aniDB',
                '</a>',
                '<a href="#" class="js-get-info">Get Info</a>'
            ])

        return anidb_str if anidb_str else ""

    def _identify_str(container):
        identify_str = None

        if container.__class__.__name__ == "Show":
            identify_str = '<a href="#" class="js-identify">Identify</a>'

        return identify_str if identify_str else ""

    @staticmethod
    def html_page(container, meta=None):
        from classes.ui.media_ui import MediaUI
        page = f'''
        <div class="container page header" data-id="{container.id()}">
            {ContainerUI._img_str(container)}
            <span class="info">
                {ContainerUI._title_str(container)}
                {ContainerUI._description_str(container)}
                <span>
                    {ContainerUI._scan_str}
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
            '      </span>',
            '      <span class="line2">',
            f'          {ContainerUI._scan_str}',
            f'          {ContainerUI._identify_str(container)}',
            '      </span>',
            '  </span>',
            '</div>\n'
        ])

        f'''
            <div class="container line js-navigation js-container" data-id="{
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
