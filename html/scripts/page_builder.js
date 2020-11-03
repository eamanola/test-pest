function parents(item, hide) {
  var ret = []

  if (item.parents && !hide) {
    ret.push('<span class="parents js-parents"{wrapper_style}>')

    for (var i = 0, il = item.parents.length; i < il; i++) {
      ret.push(
        ['<span class="js-navigation js-parent" data-id="', item.parents[i].id,
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

function anidb_link(container) {
  var ret = ""

  if (container.anidb_id)
    ret = [
      '<a href="https://anidb.net/anime/', container.anidb_id, '" ',
        'target="_blank" rel="noopener noreferrer" class="external-link ',
        'js-external-link">aniDB</a>'
    ].join("")

  return ret
}

function get_info_link(item, show_ifneeded) {
  var ret = ""

  if (item.can_identify && item.is_identified) {
    if (!show_ifneeded || (item.is_identified && !item.has_info)) {
      ret = ['<a href="#" class="js-get-info">',
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
      ret = '<a href="#" class="js-identify">Identify</a>'
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


  if (desc) {
    ret = ['<span class="description">', desc, '</span>'].join("")
  }

  return ret
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
        '<div class="actions">',
          '<a href="#" class="js-scan">Scan</a>',
          identify_link(container, false),
          anidb_link(container),
          get_info_link(container, false),
        '</div>',
      '</span>',
    '</div>'
  ]

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

  return ret.join('')
}

function container_line(container) {
  var ret = [
    '<div class="container line js-container js-navigation" ',
      'data-id="', container.id, '">',
      '<span class="left">',
        container_img(container),
        '<span class="info">',
          '<span class="line1">',
            parents(container),
            '<span class="">', container.title, '</span>',
          '</span>',
          '<span class="line2">',
            rating(container),
            container_unplayed(container),
            '<label class="js-played"><input type="checkbox" ',
              'name="js-played-', container.id ,'"',
              container.played ? ' checked="checked"' : "",
              '/><span>Played</span></label>',
          '</span>',
        '</span>',
      '</span>',
      '<span class="right">',
        '<span class="line1">',
          get_info_link(container, true),
          '<a href="#" class="js-scan">Scan</a>',
          identify_link(container, true),
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
        '<div class="actions">',
          identify_link(media, false),
          anidb_link(media),
          get_info_link(media, false),
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
      '<span class="left">',
        media_img(media),
        '<span class="info">',
          '<span class="line1">',
            parents(media, hide_parents),
            '<span>', media.title, '</span>',
          '</span>',
          '<span class="line2">',
            rating(media),
            '<a href="#" class="js-add-to-play">',
              in_add_to_play_list(media.id) ? '-Play' : '+Play',
            ,'</a>',
            '<label class="js-played"><input type="checkbox"',
              ' name="js-played-', media.id ,'"',
              media.played ? ' checked="checked"' : "",
              '/><span>Played</span></label>',
          '</span>',
        '</span>',
      '</span>',
      '<span class="right" ',
        !media.can_identify || (
          media.is_identified && media.has_info
        ) ? 'style=display:none"':'',
      '>',
        '<span class="line1">',
          get_info_link(media, true),
          identify_link(media, true),
        '</span>',
      '</span>',
    '</div>'
  ]

  return ret.join("")
}
