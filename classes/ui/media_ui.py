from classes.ui.html_ui import HTMLUI
from classes.identifiable import Identifiable

# deprecated


class MediaUI(object):

    def __init__(self):
        super(MediaUI, self).__init__()

    def _img_str(media):
        from classes.images import Images
        img_src = None
        if isinstance(media, Identifiable):
            img_src = Images.poster(media)
            class_str = "poster"

        if not img_src:
            img_src = Images.thumbnail(media, create_ifmissing=True)
            class_str = "thumbnail"

        if img_src:
            img_str = ''.join([
                '<span class="js-play-wrapper">',
                f'<img src="{img_src}" class="js-play {class_str}" />',
                '</span>'
            ])

        return img_str if img_src else ""

    _add_to_play_str = '<a href="#" class="js-add-to-play">+Play</a>'

    def _get_episode_meta(episode):
        from classes.media import Episode

        episode_meta = None
        if isinstance(episode, Episode) and episode.episode_number():
            parent = episode.parent()
            while(
                parent and
                not (isinstance(parent, Identifiable) and parent.meta())
            ):
                parent = parent.parent()

            if (
                parent and
                isinstance(parent, Identifiable) and
                parent.meta()
            ):
                episode_meta = parent.meta().get_episode(episode)

        return episode_meta

    @staticmethod
    def html_page(media):
        episode_meta = MediaUI._get_episode_meta(media)

        page = ''.join([line.lstrip() for line in [
            f'<div class="media page header js-media" data-id="{media.id()}">',
            f'  {MediaUI._img_str(media)}',
            f'  <span class="info">',
            f'''      {HTMLUI.title_html(
                        media,
                        episode_meta=episode_meta,
                        navigation=False
                    )}''',
            f'      {HTMLUI.parents_html(media)}',
            f'      {HTMLUI.description_html(media, episode_meta)}',
            f'      {HTMLUI.identify_html(media, show_ifneeded=False)}',
            f'      {HTMLUI.anidb_html(media)}',
            f'      {HTMLUI.get_info_html(media, show_ifneeded=False)}'
            '   </span>',
            '</div>'
        ]])

        return page

    @staticmethod
    def html_line(media):
        from classes.media import Movie

        episode_meta = MediaUI._get_episode_meta(media)

        get_info_str = HTMLUI.get_info_html(media)
        identify_str = HTMLUI.identify_html(media)

        if get_info_str or identify_str:
            right_style = ""
        else:
            right_style = ' style="display:none"'

        is_movie = ""
        if isinstance(media, Movie):
            is_movie = " movie"

        return ''.join(line.lstrip() for line in [
            f'<div class="media{is_movie} js-media line"',
            f' data-id="{media.id()}">',
            '   <span class="left">',
            f'      {MediaUI._img_str(media)}',
            '       <span class="info">',
            '           <span class="line1">',
            f'              {HTMLUI.parents_html(media, display_none=True)}',
            f'''            {HTMLUI.title_html(
                                media,
                                episode_meta=episode_meta
                            )}''',
            '           </span>',
            '           <span class="line2">',
            f'              {HTMLUI.rating_html(media)}',
            f'              {MediaUI._add_to_play_str}',
            f'              {HTMLUI.played_html(media, media.played())}',
            '           </span>',
            '       </span>',
            '   </span>',
            f'   <span class="right"{right_style}>',
            '       <span class="line1">',
            f'          {get_info_str}',
            f'          {identify_str}',
            '       </span>',
            '   </span>',
            '</div>\n'
        ])
