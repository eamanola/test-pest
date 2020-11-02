function onClearPlayNextListCleared(responseText) {
  document.getElementById('play-next-list').style.display = "none"
  document.getElementById("play-next-list-content").innerHTML = ""

}

function onClearPlayNextListClick(e) {
  e.preventDefault();
  e.stopPropagation();

  ajax(base_url + "/clearplaynextlist", onClearPlayNextListCleared)
}

////////////////////////////////////////////////////////////////////////////////

function onToggleToPlayClick(e) {
  var id_obj = get_data_id(e.target)
  var data_id = id_obj.data_id

  if (data_id) {
    e.preventDefault();
    e.stopPropagation();

    var list_str = sessionStorage.getItem('add-to-play-list')
    var obj_list = list_str ? JSON.parse(list_str) : []

    var in_list_index = null
    for (var i = 0, il = obj_list.length; i < il; i++) {
      if (obj_list[i].id === data_id) {
        in_list_index = i
        break
      }
    }

    if (in_list_index !== null) {
      obj_list.splice(in_list_index, 1)

      var el = document.querySelector(
        '#add-to-play-list [data-id="' + data_id + '"]'
      )
      document.getElementById('add-to-play-list').removeChild(el)

    } else {
      var obj = cache_get_item(data_id)
      if (obj) {
        obj_list.push(obj)

        var html = media_line(obj)
        var list_el = document.getElementById('add-to-play-list')
        list_el.innerHTML = list_el.innerHTML + html

        var el = document.querySelector(
          '#add-to-play-list [data-id="' + data_id + '"]'
        )
        connect(el)

      } else {
        console.log('not in cache')
      }

    }

    sessionStorage.setItem('add-to-play-list', JSON.stringify(obj_list))

    update_play_clear_buttons()

    var add_to_play_links = document.querySelectorAll(
      '[data-id="' + data_id + '"] .js-add-to-play'
    )
    for (var i = 0, il = add_to_play_links.length; i < il; i++) {
      add_to_play_links[i].innerHTML =
        (in_list_index === null ? '-Play' : '+Play')
    }
  }

  return false
}

function update_play_clear_buttons() {
  var list_str = sessionStorage.getItem('add-to-play-list')
  var list = list_str ? JSON.parse(list_str) : []

  play_button = document.getElementById('play-button');
  play_button.innerHTML = "Play(" + list.length + ")"

  clear_button =  document.getElementById('clear-add-to-play-list-button')

  play_button.style.display = clear_button.style.display =
    list.length ? "initial" : "none"
}

function create_add_to_play_list() {
  var list_str = sessionStorage.getItem('add-to-play-list')
  var obj_list = list_str ? JSON.parse(list_str) : []

  var html = []
  for (var i = 0, il = obj_list.length; i < il; i ++) {
    html.push(media_line(obj_list[i]))
  }

  var list_el = document.getElementById('add-to-play-list')
  list_el.innerHTML = html.join("")
  connect(list_el)
  update_play_clear_buttons()
}

////////////////////////////////////////////////////////////////////////////////

function onGetInfoCompleted(responseText) {
  var item = JSON.parse(responseText)

  update_items(item)
}

function onGetInfoClick(e) {

  var id_obj = get_data_id(e.target)
  var data_id = id_obj.data_id
  var type = id_obj.type

  if (type && data_id && (type === "container" || type === "media")) {
    e.preventDefault();
    e.stopPropagation();
    var url = [
      base_url,
      "/info",
      '/', type.substring(0, 1),
      '/', data_id
    ].join("")

    ajax(url, onGetInfoCompleted)

    var query = '[data-id="' + data_id + '"] .js-get-info'
    var el = document.querySelectorAll(query)[0]
    el.innerHTML = "searching"
    el.removeEventListener('click', onGetInfoClick, false)
  }
}

////////////////////////////////////////////////////////////////////////////////

function onPlayedSaved(responseText) {
  var item = JSON.parse(responseText)

  // no actions required for media items
  if (item.unplayed_count !== undefined) {
    var el = null, els = document.querySelectorAll(
      '[data-id="' + item.data_id + '"] .js-unplayed'
    )

    for (var i = 0, il = els.length; i < il; i++) {
      el = els[i]
      el.outerHTML = container_unplayed({unplayed_count: item.unplayed_count})
    }
  }
}

function onPlayedClick(e) {
  var id_obj = get_data_id(e.target)
  var data_id = id_obj.data_id
  var type = id_obj.type

  if (data_id && type && (type === "container" || type === "media")) {
    e.stopPropagation();

    var checkbox = document.querySelector(
      '[data-id="' + data_id + '"] .js-played input'
    )

    var url = [
        base_url,
        "/played",
        '/', type.substring(0, 1),
        '/', checkbox.checked ? "1" : "0",
        '/', data_id
    ].join("")

    ajax(url, onPlayedSaved)
  }

  return false
}

////////////////////////////////////////////////////////////////////////////////

function onPlayConfirmed(responseText) {
  console.log(responseText.replace(/\s+/g, " "))
}

function onPlaySingleClick(e) {
  var data_id = get_data_id(e.target).data_id

  if (data_id) {
    if (e && e.preventDefault) {
      e.preventDefault();
      e.stopPropagation();
    }
    ajax(base_url + '/play/' + data_id, onPlayConfirmed)
  }

  return false
}

function onPlayClick(e) {
  if (e && e.preventDefault) {
    e.preventDefault();
    e.stopPropagation();
  }

  var list_str = sessionStorage.getItem('add-to-play-list')
  var obj_list = list_str ? JSON.parse(list_str) : []
  var media_ids = []
  for (var i = 0, il = obj_list.length; i < il; i++) {
    media_ids.push(obj_list[i].id)
  }
  if (list_str) {
    ajax(base_url + '/play/' + media_ids.join(","), onPlayConfirmed)
  }

  return false
}

function onClearPlayClick(e) {
  e.preventDefault();
  e.stopPropagation();

  sessionStorage.removeItem('add-to-play-list')

  document.getElementById('add-to-play-list').innerHTML = ""

  update_play_clear_buttons()

  var els = document.querySelectorAll('.js-add-to-play')
  for (var i = 0, il = els.length; i < il; i ++) {
    if (els[i].innerHTML !== "+Play") {
      els[i].innerHTML = "+Play"
    }
  }

  return false
}

////////////////////////////////////////////////////////////////////////////////

function onIdentifyError(data_id) {
  var el = document.querySelector('[data-id="' + data_id + '"] .js-identify')
  el.innerHTML = "Identify"
  el.addEventListener('click', onIdentifyClick, false)
}

function onIdentifyCompleted(responseText) {
  var item = JSON.parse(responseText)

  if (item.identified === true){
    update_items(item)
  } else {
    onIdentifyError(item.data_id)
  }
}

function onIdentifyClick(e) {
  var id_obj = get_data_id(e.target)
  var data_id = id_obj.data_id
  var type =  id_obj.type
  if (data_id && type && (type === "container" || type === "media")) {
    e.preventDefault();
    e.stopPropagation();

    ajax(
      [
        base_url, '/identify', '/', type.substring(0, 1), '/', data_id
      ].join(""),
      onIdentifyCompleted,
      (
        function (data_id) {
          return function() {
            onIdentifyError(data_id)
          }
        }
      )(data_id))

    var query = '[data-id="' + data_id + '"] .js-identify'
    var el = document.querySelectorAll(query)[0]
    el.innerHTML = "Identifying"
    el.removeEventListener('click', onIdentifyClick, false)
  }

  return false
}

////////////////////////////////////////////////////////////////////////////////

function onScanError(data_id) {
  var query = '[data-id="' + data_id + '"] .js-scan'
  var el = document.querySelector(query)
  el.innerHTML = "Scan"
  el.addEventListener('click', onScanClick, false)
}

function onScanCompleted(responseText) {
  var item = JSON.parse(responseText)

  update_items(item)
}

function onScanClick(e) {
  var id_obj = get_data_id(e.target)
  var data_id = id_obj.data_id
  if (data_id) {
    e.preventDefault();
    e.stopPropagation();

    ajax(
      base_url + '/scan/' + data_id,
      onScanCompleted,
      (
        function (data_id) {
          return function() {
            onScanError(data_id)
          }
        }
      )(data_id)
    )

    var query = '[data-id="' + data_id + '"] .js-scan'
    var el = document.querySelectorAll(query)[0]
    el.innerHTML = "Scanning"
    el.removeEventListener('click', onScanClick, false)
  }

  return false
}

////////////////////////////////////////////////////////////////////////////////

function onNavigationClick(e) {
  var id_obj = get_data_id(e.target)
  var type = id_obj.type
  var data_id = id_obj.data_id

  if (type && data_id) {
    e.preventDefault();
    e.stopPropagation();

    if (type == "container") {
      getContainer(data_id)
    } else if (type == "media") {
      getMedia(data_id)
    }
  }

  return false
}

////////////////////////////////////////////////////////////////////////////////

function connect(parent) {

  var navigation_items = parent.querySelectorAll('.js-navigation')
  for (var i = 0, il = navigation_items.length; i < il; i++) {
    navigation_items[i].addEventListener('click', onNavigationClick, false)
  }

  var scan_items = parent.querySelectorAll('.js-scan')
  for (var i = 0, il = scan_items.length; i < il; i++) {
    scan_items[i].addEventListener('click', onScanClick, false)
  }

  var identify_items = parent.querySelectorAll('.js-identify')
  for (var i = 0, il = identify_items.length; i < il; i++) {
    identify_items[i].addEventListener('click', onIdentifyClick, false)
  }

  var play_items = parent.querySelectorAll('.js-play')
  for (var i = 0, il = play_items.length; i < il; i++) {
    play_items[i].addEventListener('click', onPlaySingleClick, false)
  }

  var played_items = parent.querySelectorAll('.js-played')
  for (var i = 0, il = played_items.length; i < il; i++) {
    played_items[i].addEventListener('click', onPlayedClick, false)
  }

  var get_info_items = parent.querySelectorAll('.js-get-info')
  for (var i = 0, il = get_info_items.length; i < il; i++) {
    get_info_items[i].addEventListener('click', onGetInfoClick, false)
  }

  var add_to_play_items = document.querySelectorAll('.js-add-to-play')
  for (var i = 0, il = add_to_play_items.length; i < il; i++) {
    add_to_play_items[i].addEventListener('click', onToggleToPlayClick, false)
  }
}

////////////////////////////////////////////////////////////////////////////////

function onHomeReceived(responseText) {
  var data = JSON.parse(responseText)

  onPlayNextListReceived(JSON.stringify(data.play_next_list))

  var media_libraries = data.media_libraries
  var page = [], media_library = null
  for (var i = 0, il = media_libraries.length; i < il; i ++) {
    media_library = media_libraries[i]

    page.push(container_page(media_library))

    cache.push(media_library)
  }
  var page_el = document.getElementById('page')
  page_el.innerHTML = page.join("")
  connect(page_el)
}

function home() {
  ajax(base_url, onHomeReceived)
}

////////////////////////////////////////////////////////////////////////////////
function onContainerReceived(responseText) {
  container = JSON.parse(responseText)
  cache.push(container)
  document.getElementById('page').innerHTML =
    container_page(container)
  connect(document.body)
}

function getContainer(container_id, dont_push) {
  if (!container_id)
    container_id = "d16c4b170f395bcdeaedcd5c9786eb01"

  if (!dont_push) {
    history.pushState({
      type: "container",
      data_id: container_id,
    }, "")
  }

  ajax(
    base_url + '/c/' + container_id,
    onContainerReceived
  )
}

////////////////////////////////////////////////////////////////////////////////

function onMediaReceived(responseText) {
  media = JSON.parse(responseText)
  cache.push(media)
  document.getElementById('page').innerHTML =
    media_page(media)
  connect(document.body)
}

function getMedia(media_id, dont_push) {
  if (!dont_push) {
    history.pushState({
      type: "media",
      data_id: media_id
    }, "")
  }

  ajax(
    base_url + '/m/' + media_id,
    onMediaReceived
  )
}

////////////////////////////////////////////////////////////////////////////////

function onPlayNextListReceived(responseText) {
  playNextList = JSON.parse(responseText)

  if (playNextList.length == 0) {
    document.getElementById('play-next-list').style.display = 'none'
  }
  else {
    play_next_list_str = []
    for (var i = 0, il = playNextList.length; i < il; i++) {
      cache.push(playNextList[i])

      play_next_list_str.push(media_line(playNextList[i], {hide_parents: false}))
    }
    var el = document.getElementById('play-next-list-content')
    el.innerHTML = play_next_list_str.join("")
    connect(el)

    document.getElementById('play-next-list').style.display = 'initial'
  }
}

function getPlayNextList() {
  ajax(base_url + '/playnextlist', onPlayNextListReceived)
}


////////////////////////////////////////////////////////////////////////////////

function in_add_to_play_list(item_id) {
  var list_str = sessionStorage.getItem('add-to-play-list')
  var obj_list = list_str ? JSON.parse(list_str) : []

  var found = false

  for (var i = 0, il = obj_list.length; i < il; i ++){
    if (obj_list[i].id === item_id) {
      found = true
      break
    }
  }

  return found
}

cache = []
function cache_get_item(item_id) {
  var ret = null

  for (var j = 0, jl = cache.length; j < jl; j++) {
    cache_item = cache[j]

    if (cache_item.id === item_id) {
      ret = cache_item
    }

    if (ret === null) {
      if (cache_item.containers) {
        for (var i = 0, il = cache_item.containers.length; i < il; i++) {
          if (cache_item.containers[i].id === item_id) {
            ret = cache_item.containers[i];
            break;
          }
        }
      }
    }

    if (ret === null) {
      if (cache_item.media) {
        for (var i = 0, il = cache_item.media.length; i < il; i++) {
          if (cache_item.media[i].id === item_id) {
            ret = cache_item.media[i];
            break;
          }
        }
      }
    }

    if (ret !== null)
      break
  }

  return ret
}

function ajax(url, callback, errorcallback) {
  var xhttp = new XMLHttpRequest();
  xhttp.onreadystatechange = function() {
    if (this.readyState == 4) {
      if (this.status == 200) {
        callback(this.responseText)
      } else /* if (this.status == 400 || this.status == 404) */ {
        if (typeof(errorcallback) == "function") {
          errorcallback(this.responseText)
        }
      }
    }
  };
  xhttp.open("GET", url, true);
  xhttp.send();
}

function get_data_id(el) {
  var type = null
  var data_id = null

  while(el && !el.hasAttribute('data-id')) {
    el = el.parentNode
  }

  if (el) {
    if(el.classList.contains('js-container') ||
        el.classList.contains('js-parent'))
      type = "container"
    else if(el.classList.contains('js-media'))
      type = "media"

    data_id = el.getAttribute('data-id')
  }

  return {
    'type': type,
    'data_id': data_id
  }
}

var base_url = ""
if (window.location.port) {
  base_url = window.location.origin
} else {
  var GET_params_str = window.location.search.substr(1),
    GET_params = GET_params_str.split("&")
  for (var i = 0, il = GET_params.length; i < il; i++) {
    if (GET_params[i].startsWith('api_url')) {
      base_url = GET_params[i].split("=")[1]
    }
  }
}

function updatePage(state) {
  if (!state) state = history.state

  if (state == null){
    home()
  } else if (state.type == "container") {
    getContainer(state.data_id, true)
  } else if (state.type == "media") {
    getMedia(state.data_id, true)
  }
}

function update_items(item) {
  if (!item) return

  var query = [
    '.js-container[data-id="' + item.id + '"]',
    '.js-media[data-id="' + item.id + '"]',
  ].join(",")
  var els = document.querySelectorAll(query)

  for (var i = 0, il = els.length; i < il; i++) {
    if (els[i].classList.contains('page')) {
      return updatePage();
    }
  }

  for (var i = 0, il = els.length; i < il; i++) {
    el = els[i]
    content = null
    if (el.classList.contains('line')) {
      if (el.classList.contains('js-container')) {
        content = container_line(item)
      } else if (el.classList.contains('js-media')) {
        content = media_line(item)
      }
    }

    if (content) {
      el.outerHTML = content
    }
  }

  var els = document.querySelectorAll(query)
  for (var i = 0, il = els.length; i < il; i++) {
    connect(els[i])
  }
}

window.addEventListener("popstate", function(e) {
  updatePage(e.state)
}, false);

(function inits(){
  var play_button = document.getElementById('play-button')
  play_button.addEventListener('click', onPlayClick, false)

  var clear_play_button =
    document.getElementById('clear-add-to-play-list-button')
  clear_play_button.addEventListener('click', onClearPlayClick, false)

  var clear_play_next_list_button =
    document.getElementById('clear-play-next-list-button')
  clear_play_next_list_button
    .addEventListener('click', onClearPlayNextListClick, false)

  home()
  create_add_to_play_list()
})()
