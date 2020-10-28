from classes.identifiable import Identifiable
from classes.container import MediaLibrary, Show, Season, Extra
from classes.media import Media, Movie, Episode
from classes.images import Images


class DictItem(object):
    def __init__(self):
        super(DictItem, self).__init__()

    def dict(item):
        ret = {
            'id': item.id(),
            'title': item.title()
        }

        if item.parent():
            ret['parent'] = item.parent().id()

        if isinstance(item, Identifiable):
            ret = {**ret, **_identifiable_dict(item)}

        parents = _parents(item)
        if len(parents) > 0:
            ret['parents'] = parents

        return ret


class DictContainer(object):
    def __init__(self):
        super(DictContainer, self).__init__()

    def dict(container):
        ret = {
            **DictItem.dict(container),
            'played': container.unplayed_count() == 0,
            'unplayed_count': container.unplayed_count(),
            'containers': [
                DictContainer.dict(c) for c in container.containers
            ],
            'media': [
                DictMedia.dict(m) for m in container.media
            ]
        }

        return ret


class DictMedia(object):

    def __init__(self):
        super(DictMedia).__init__()

    def dict(media):
        ret = {
            **DictItem.dict(media),
            'played': media.played(),
            'thumbnail': Images.thumbnail(media),
            'is_movie': isinstance(media, Movie)
        }

        if isinstance(media, Episode):
            episode_meta = _episode_meta(media)
            if episode_meta:
                summary = episode_meta.summary()
                if summary:
                    ret['summary'] = summary

                if not media.is_extra():
                    ret['title'] = '. '.join([
                        str(episode_meta.episode_number()),
                        episode_meta.title()
                    ])

        return ret


def _identifiable_dict(identifiable):
    ret = {}
    ret['poster'] = Images.poster(identifiable)

    anidb_id = _anidb_id(identifiable)
    if anidb_id:
        ret['anidb_id'] = anidb_id

    rating = _rating(identifiable)
    if rating:
        ret['rating'] = rating

    description = _description(identifiable)
    if description:
        ret['description'] = description

    ret['can_identify'] = _can_identify(identifiable)
    ret['is_identified'] = _is_identified(identifiable)
    ret['has_info'] = _has_info(identifiable)

    if identifiable.meta() and identifiable.meta().title():
        ret['title'] = identifiable.meta().title()

    return ret


def _anidb_id(identifiable):
    from classes.ext_apis.anidb import AniDB

    if AniDB.KEY in identifiable.ext_ids():
        anidb_id = identifiable.ext_ids()[AniDB.KEY]
    else:
        anidb_id = None

    return anidb_id


def _rating(identifiable):
    rating = None

    if identifiable.meta() and identifiable.meta().rating():
        rating = identifiable.meta().rating()

    return rating


def _description(identifiable):
    description = None

    if (
        identifiable.meta()
        and identifiable.meta().description()
    ):
        description = identifiable.meta().description()

    return description


def _episode_meta(episode):
    episode_meta = None

    parent = episode.parent()
    while parent and isinstance(parent, Identifiable):
        if parent.meta():
            episode_meta = parent.meta().get_episode(episode)
            if episode_meta:
                break

        parent = parent.parent()

    return episode_meta


def _parents(item):
    parents = []

    parent = item.parent()
    while parent and isinstance(parent, (Show, Season, Extra)):
        parents.append({
            'id': parent.id(),
            'title': parent.title()
        })

        parent = parent.parent()

    parents.reverse()
    return parents


def _can_identify(identifiable):
    return (identifiable.__class__.__name__ in ("Movie", "Show"))


def _is_identified(identifiable):
    return len(identifiable.ext_ids()) > 0


def _has_info(identifiable):
    return identifiable.meta() is not None
