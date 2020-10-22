from classes.container import Container, MediaLibrary, Show, Season, Extra
from classes.media import Episode, Movie
from classes.identifiable import Identifiable


def compare_containers(con1, con2):
    return (
        (
            not isinstance(con1, (MediaLibrary, Show, Season, Extra))
            or (con1.id() == con2.id())
        )
        and (con1.__class__.__name__ == con2.__class__.__name__)
        and (len(con1.containers) == len(con2.containers))
        and (len(con1.media) == len(con2.media))
        and (
            (not con1.parent() and not con2.parent())
            or (con1.parent().id() == con2.parent().id())
        )
        and (
            not isinstance(con1, MediaLibrary)
            or (con1.path() == con2.path())
        )
        and (
            not isinstance(con1, Show)
            or (con1.show_name() == con2.show_name())
        )
        and (
            not isinstance(con1, Season)
            or con1.season_number() == con2.season_number()
        )
        and (
            not isinstance(con1, Identifiable)
            or compare_identifiables(con1, con2)
        )
    )


def compare_identifiables(ide1, ide2):
    return (
        (ide1.id() == ide2.id())
        and (ide1.year() == ide2.year())
        and (len(ide1.ext_ids()) == len(ide2.ext_ids()))
        and (
            not ide1.meta()
            or compare_meta(ide1.meta(), ide2.meta())
        )
    )


def compare_meta(meta1, meta2):
    return (
        (meta1.id() == meta2.id())
        and (meta1.title() == meta2.title())
        and (meta1.rating() == meta2.rating())
        and (meta1.image_name() == meta2.image_name())
        and (
            not meta1.episodes()
            or compare_meta_episodes(meta1.episodes(), meta2.episodes())
        )
        and (meta1.description() == meta2.description())
    )


def compare_meta_episodes(epi1, epi2):
    return len(epi1) == len(epi2)  # TODO


def compare_media(med1, med2):
    return (
        (med1.file_path() == med2.file_path())
        and (
            not med1.parent()
            or med1.parent().id() == med2.parent().id()
        )
        and (
            not isinstance(med1, Movie)
            or (med1.title() == med2.title())
        )
        and (
            not isinstance(med1, Episode)
            or (
                (med1.episode_number() == med2.episode_number())
                and (med1.is_oad() == med2.is_oad())
                and (med1.is_ncop() == med2.is_ncop())
                and (med1.is_nced() == med2.is_nced())
                and (med1.is_ova() == med2.is_ova())
            )
        )
        and compare_media_states(med1, med2)
        and (
            not isinstance(med1, Identifiable)
            or compare_identifiables(med1, med2)
        )
    )


def compare_media_states(med1, med2):
    return (med1.played() == med2.played())
