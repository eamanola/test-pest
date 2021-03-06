function parents(item, hide) {
  var ret = []

  if (item.parents && !hide) {
    ret.push('<span class="parents js-parents">')

    for (var i = 0, il = item.parents.length; i < il; i++) {
      ret.push(
        ['<span class="navigation js-navigation js-parent" data-id="', item.parents[i].id,
        '">[', item.parents[i].title, ']</span>'].join("")
      )
    }

    ret.push('</span>')
  }

  return ret.join("")
}

function container_img(container) {
  var ret = ""

  if (container.poster)
    ret = [
      '<img src="', base_url, '/', container.poster,'" class="poster" />'
    ].join('')

  return ret
}

function media_img(media) {
  class_name = media.poster ? "poster": "thumbnail"
  src = media.poster ? media.poster : media.thumbnail

  return [
    '<span class="js-play-wrapper">',
    '<img src="', base_url, '/', src, '" class="js-play ', class_name, '" />',
    '</span>'
  ].join("")
}

function anidb_link(item) {
  var ret = ""

  if (item.anidb_id)
    ret = [
      '<a href="https://anidb.net/anime/', item.anidb_id, '" ',
        'target="_blank" rel="noopener noreferrer" class="external-link ',
        'js-external-link">aniDB</a>'
    ].join("")

  return ret
}

function omdb_link(item) {
  var ret = ""

  if (item.omdb_id)
    ret = [
      '<a href="https://www.imdb.com/title/', item.omdb_id, '/" ',
        'target="_blank" rel="noopener noreferrer" class="external-link ',
        'js-external-link">IMDb</a>'
    ].join("")

  return ret
}

function get_info_link(item, show_ifneeded) {
  var ret = ""

  if (item.can_identify && item.is_identified) {
    if (!show_ifneeded || (item.is_identified && !item.has_info)) {
      ret = ['<a href="#" class="action js-get-info">',
        item.has_info ? "Update Info" : "Get Info",
      '</a>'].join("")
    }
  }

  return ret
}

function identify_link(item, show_ifneeded) {
  var ret = ""

  if (item.can_identify) {
    if (!show_ifneeded || !item.is_identified) {
      ret = '<a href="#" class="action js-identify">Identify</a>'
    }
  }

  return ret
}

function rating(item) {
  var ret = ""

  if (item.rating)
    ret = ['<span class="rating">',
            item.rating,' / 10',
          '</span>'].join('')

  return ret
}

function container_unplayed(container) {
  var ret = [
    '<span class="unplayed js-unplayed" ',
      'data-unplayed-count="', container.unplayed_count, '">',
      '[', container.unplayed_count, ']',
    '</span>'
    ].join("")

  return ret
}

function description(item) {
  var ret = ""

  var desc = ""
  if (item.description)
    desc = item.description
  else if (item.summary)
    desc = item.summary

  desc = desc.replace(
    /(http:\/\/anidb.net[^\s]+)\s\[([^\]]+)\]/g,
    ['<a href="$1" target="_blank" rel="noopener noreferrer"',
    'class="external-link js-external-link">$2</a>'].join("")
  )

  if (desc) {
    ret = ['<span class="description">', desc, '</span>'].join("")
  }

  return ret
}

function play(media){
  return ['<a href="#" class="action mobile-play js-play">Play</a>'].join("")
}

function played(item) {
  return [
    '<label class="action played js-played"><input type="checkbox" ',
    'name="js-played-', item.id ,'"',
    item.played ? ' checked="checked"' : "",
    '/><span>Played</span>',
    item.unplayed_count !== undefined ? container_unplayed(item) : "",
    '</label>'
  ].join("")
}

function container_page(container) {
  var ret = [
    '<div class="container js-container page header" ',
      'data-id="', container.id, '">',
      container_img(container),
      '<span class="info">',
        '<span>', container.title, '</span>',
        parents(container),
        description(container),
        '<div>',
          '<a href="#" class="action js-scan">Scan</a>',
          identify_link(container, false),
          get_info_link(container, false),
          anidb_link(container),
          omdb_link(container),
        '</div>',
      '</span>',
    '</div>'
  ]

  ret.push('<div>') // child container

  container.containers.sort(function(a, b) {
    if (a.unplayed_count == 0 && b.unplayed_count != 0)
      return 1
    else if (a.unplayed_count != 0 && b.unplayed_count == 0)
      return -1
    else if (a.unplayed_count < b.unplayed_count)
      return -1
    else if (a.unplayed_count > b.unplayed_count)
      return 1
    else if (a.title < b.title)
      return -1
    else if (a.title > b.title)
      return 1
    else
      return 0
  })

  for (var i = 0, il = container.containers.length; i < il; i++)
    ret.push(container_line(container.containers[i]))

  container.media.sort(function(a, b){
    if (a.episode_number || b.episode_number) {
      if (a.episode_number && !b.episode_number)
        return -1
      else if (!a.episode_number && b.episode_number)
        return 1
      else if (a.episode_number < b.episode_number)
        return -1
      else if (a.episode_number > b.episode_number)
        return 1
    }
    else if (!a.played && b.played)
      return -1
    else if (a.played && !b.played)
      return 1
    else if (a.title < b.title)
      return -1
    else if (a.title > b.title)
      return 1
    else
      return 0
  })

  for (var i = 0, il = container.media.length; i < il; i++)
    ret.push(media_line(container.media[i]))

  ret.push('</div>')  // end child container

  return ret.join('')
}

function container_line(container) {
  var ret = [
    '<div class="container line js-container js-navigation" ',
      'data-id="', container.id, '">',
      container_img(container),
      '<span class="left">',
        '<span class="info-line">',
          parents(container),
          '<span class="navigation title">', container.title, '</span>',
        '</span>',
        '<span class="info-line">',
          rating(container),
          played(container),
        '</span>',
      '</span>',
      '<span class="right">',
        '<span class="info-line">',
          '<a href="#" class="action js-scan">Scan</a>',
          identify_link(container, true),
          get_info_link(container, true),
        '</span>',
      '</span>',
    '</div>'].join("")

  return ret
}

function media_page(media) {

  var ret = [
    '<div class="media page header js-media" data-id="', media.id, '">',
      media_img(media),
      '<span class="info">',
        '<span>', media.title, '</span>',
        parents(media),
        description(media),
        '<div>',
          identify_link(media, false),
          get_info_link(media, false),
          anidb_link(media),
          omdb_link(media),
        '</div>',
      '</span>',
    '</div>'
  ]

  return ret.join("")
}

function media_line(media, opts) {
  hide_parents = opts && opts.hide_parents !== undefined ? opts.hide_parents : true
  var ret = [
    '<div class="media js-navigation ',
      media.is_movie ? "movie " : "", 'js-media line" ',
    'data-id="', media.id, '">',
      media_img(media),
      '<span class="left">',
        '<span class="info-line">',
          parents(media, hide_parents),
          '<span class="navigation title">', media.title, '</span>',
        '</span>',
        '<span class="info-line">',
          rating(media),
          '<a href="#" class="action js-add-to-play">',
            in_add_to_play_list(media.id) ? '-Play' : '+Play',
          ,'</a>',
          played(media),
          play(media),
        '</span>',
      '</span>',
      '<span class="right" ',
        !media.can_identify || (
          media.is_identified && media.has_info
        ) ? 'style=display:none"':'',
      '>',
        '<span class="info-line">',
          get_info_link(media, true),
          identify_link(media, true),
        '</span>',
      '</span>',
    '</div>'
  ]

  return ret.join("")
}
