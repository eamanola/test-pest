storage = sessionStorage

function ajax(url, callback) {
  var xhttp = new XMLHttpRequest();
  xhttp.onreadystatechange = function() {
    if (this.readyState == 4 && this.status == 200) {
      callback(this.responseText)
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

function updatePage() {
  var url = "/" + window.location.search
  ajax(
    url,
    function updatePageDataReceived(responseText) {
      document.body.innerHTML = responseText

      init()
    }
  )
}
///////////////////////////////////////////////////////////////////////////////
function onNavigationClick(e) {
  e.preventDefault();

  var id_obj = get_data_id(e.target)
  var type = id_obj.type
  var data_id = id_obj.data_id
  var url = undefined

  if (type && data_id) {
    if (type == "container") {
      url =  '/?c=' + data_id
    } else if (type == "media") {
      url =  '/?m=' + data_id
    }
  }

  if (url) {
    if (window.location.pathname + window.location.search != url)
      window.location.href = url
  }

  return false
}
///////////////////////////////////////////////////////////////////////////////

function onScanCompleted(responseText) {
  return updatePage();

  console.log(responseText.replace(/\s+/g, " "))

  var data_id = response.data_id
  var query = '[data-id="' + data_id + '"] .js-scan'
  var el = document.querySelectorAll(query)[0]
  el.innerHTML = "Scan"
  el.addEventListener('click', onScanClick, false)
}

function onScanClick(e) {
  e.preventDefault();

  var id_obj = get_data_id(e.target)
  var data_id = id_obj.data_id
  if (data_id) {
    ajax('/?s=' + data_id, onScanCompleted)

    var query = '[data-id="' + data_id + '"] .js-scan'
    var el = document.querySelectorAll(query)[0]
    el.innerHTML = "Scanning"
    el.removeEventListener('click', onScanClick, false)
  }

  return false
}
///////////////////////////////////////////////////////////////////////////////

function onIdentifyCompleted(responseText) {
  return updatePage();
  console.log(responseText.replace(/\s+/g, " "))
}

function onIdentifyClick(e) {
  e.preventDefault();

  var id_obj = get_data_id(e.target)
  var data_id = id_obj.data_id
  if (data_id) {
    ajax('/?i=' + data_id, onIdentifyCompleted)

    var query = '[data-id="' + data_id + '"] .js-identify'
    var el = document.querySelectorAll(query)[0]
    el.innerHTML = "identifying"
    el.removeEventListener('click', onIdentifyClick, false)
  }

  return false
}
///////////////////////////////////////////////////////////////////////////////

function onPlayConfirmed(responseText) {
  console.log(responseText.replace(/\s+/g, " "))
}

function onPlayClick(e) {
  if (e && e.preventDefault)
    e.preventDefault();

  var list_str = storage.getItem('add-to-play-list')
  if (list_str) {
    ajax('/?p=' + list_str, onPlayConfirmed)
  }

  return false
}
///////////////////////////////////////////////////////////////////////////////

function onGetInfoCompleted(responseText) {
  return updatePage();
  console.log(responseText.replace(/\s+/g, " "))
}

function onGetInfoClick(e) {
  e.preventDefault()

  var id_obj = get_data_id(e.target)
  var data_id = id_obj.data_id
  var type = id_obj.type
  var url = undefined

  if (type && data_id) {
    if (type == "container") {
      url =  '/?gic=' + data_id
    } else if (type == "media") {
      url =  '/?gim=' + data_id
    }
  }

  if (url) {
    ajax(url, onGetInfoCompleted)

    var query = '[data-id="' + data_id + '"] .js-get-info'
    var el = document.querySelectorAll(query)[0]
    el.innerHTML = "searching"
    el.removeEventListener('click', onGetInfoClick, false)
  }

  return false
}
///////////////////////////////////////////////////////////////////////////////

function connect_media_items(parent) {
  var add_to_play_items = parent.querySelectorAll('.js-add-to-play')
  for (var i = 0, il = add_to_play_items.length; i < il; i++) {
    add_to_play_items[i].addEventListener('click', onToggleToPlayClick, false)
  }

  var played_items = parent.querySelectorAll('.js-played')
  for (var i = 0, il = played_items.length; i < il; i++) {
    played_items[i].addEventListener('click', onPlayedClick, false)
  }
}

function disconnect_media_items(parent) {
  var add_to_play_items = parent.querySelectorAll('.js-add-to-play')
  for (var i = 0, il = add_to_play_items.length; i < il; i++) {
    add_to_play_items[i].removeEventListener(
      'click', onToggleToPlayClick, false
    )
  }

  var played_items = parent.querySelectorAll('.js-played')
  for (var i = 0, il = played_items.length; i < il; i++) {
    played_items[i].removeEventListener('click', onPlayedClick, false)
  }
}
///////////////////////////////////////////////////////////////////////////////

function update_played_items(data_id, checked) {
  var query = '[data-id="'+data_id+'"] .js-played'
  var all = document.querySelectorAll(query)

  if (checked) {
      for (var i = 0, il = all.length; i < il; i++) {
        all[i].setAttribute("checked", "checked")
        all[i].checked = true
      }
  } else {
      for (var i = 0, il = all.length; i < il; i++) {
        all[i].removeAttribute("checked")
        all[i].checked = false
      }
  }

  storage.setItem(
    'add-to-play-list-html',
    document.getElementById('add-to-play-list').innerHTML
  )
}

function onPlayedSaved(responseText) {
  console.log(responseText.replace(/\s+/g, " "));
}

function onPlayedClick(e) {
  var id_obj = get_data_id(e.target)
  var data_id = id_obj.data_id

  if (data_id) {
    var url = ["/?", e.target.checked ? "pa" : "pr", "=", data_id].join("")
    ajax(url, onPlayedSaved)

    update_played_items(data_id, e.target.checked)
  }

  return false
}
///////////////////////////////////////////////////////////////////////////////

function update_play_clear_buttons() {
  var list_str = storage.getItem('add-to-play-list')
  var list = list_str ? list_str.split(",") : []

  play_button = document.getElementById('play-button');
  play_button.innerHTML = "Play(" + list.length + ")"

  clear_button =  document.getElementById('clear-add-to-play-list-button')

  play_button.style.display = clear_button.style.display =
    list.length ? "initial" : "none"
}

function update_add_to_play_list() {
  var html = storage.getItem('add-to-play-list-html') || ""
  var to_play_list = document.getElementById('add-to-play-list')
  to_play_list.innerHTML = html

  if (html) {
    setTimeout(function(){
      var parents = to_play_list.querySelectorAll('.js-parents')
      for(var i = 0, il = parents.length; i < il; i++)
        parents[i].style.display = "initial"

      connect_media_items(to_play_list)
    }, 0)
  }
}
///////////////////////////////////////////////////////////////////////////////

function onClearPlayClick(e) {
  e.preventDefault();

  disconnect_media_items(document.getElementById('add-to-play-list'))

  storage.removeItem('add-to-play-list')
  storage.removeItem('add-to-play-list-html')

  update_add_to_play_list()
  update_play_clear_buttons()
  update_add_to_play_items()

  return false
}
///////////////////////////////////////////////////////////////////////////////


function onToggleToPlayClick(e) {
  e.preventDefault();

  var id_obj = get_data_id(e.target)
  var data_id = id_obj.data_id

  if (data_id) {
    // update storage
    var list_str = storage.getItem('add-to-play-list')
    var list = list_str ? list_str.split(",") : []

    var index = list.indexOf(data_id)
    if (index === -1) {
      list.push(data_id)
    } else {
      list.splice(index, 1)
    }

    storage.setItem('add-to-play-list', list.join(","))

    // update play_clear_buttons
    update_play_clear_buttons()

    // update page .js-add-to-play
    update_add_to_play_items('[data-id="' + data_id + '"]')

    // update #add-to-play-list
    if (list.indexOf(data_id) !== -1) {
      copy_to_play_list(data_id)
    } else {
      remove_from_play_list(data_id)
    }
  }

  return false
}

function update_add_to_play_items(parent_query) {
  var list_str = storage.getItem('add-to-play-list')
  var list = list_str ? list_str.split(",") : []

  var add_to_play_items = null, data_id = null
  var query = [parent_query || "", '.js-add-to-play'].join(" ")
  add_to_play_items = document.body.querySelectorAll(query)

  for (var i = 0, il = add_to_play_items.length; i < il; i++) {
    data_id = get_data_id(add_to_play_items[i]).data_id

    if (data_id && list.indexOf(data_id) !== -1) {
      add_to_play_items[i].innerHTML = "-Play"
    } else {
      add_to_play_items[i].innerHTML = "+Play"
    }
  }
}

function copy_to_play_list(data_id) {
  var query = '.js-media[data-id="' + data_id + '"]'
  var media_item = document.querySelectorAll(query)[0]

  if (media_item){
    var copy = media_item.cloneNode(true)
    var parents = copy.querySelectorAll('.js-parents')
    for(var i = 0, il = parents.length; i < il; i++)
      parents[i].style.display = "initial"
    connect_media_items(copy)

    var navigation_items = copy.querySelectorAll('.js-navigation')
    for (var i = 0, il = navigation_items.length; i < il; i++) {
      navigation_items[i].addEventListener('click', onNavigationClick, false)
    }

    document.getElementById('add-to-play-list').appendChild(copy)

    storage.setItem(
      'add-to-play-list-html',
      document.getElementById('add-to-play-list').innerHTML
    )
  }
}

function remove_from_play_list(data_id) {

  var query = '#add-to-play-list .js-media[data-id="' + data_id + '"]'
  var media_item = document.querySelectorAll(query)[0]
  if (media_item) {
    disconnect_media_items(media_item)
    media_item.parentNode.removeChild(media_item)

    storage.setItem(
      'add-to-play-list-html',
      document.getElementById('add-to-play-list').innerHTML
    )
  }
}

function show_play_next_list_parents() {
  var parents = document.querySelectorAll('#play-next-list .js-parents')
  for(var i = 0, il = parents.length; i < il; i++)
    parents[i].style.display = "initial"
}


function init() {
  var play_item = document.getElementById('play-button')
  play_item.addEventListener('click', onPlayClick, false)

  var clear_play_item = document.getElementById('clear-add-to-play-list-button')
  clear_play_item.addEventListener('click', onClearPlayClick, false)

  update_add_to_play_list() // put before update_add_to_play_items
  update_play_clear_buttons()
  update_add_to_play_items()
  connect_media_items(document.body)

  var identify_items = document.querySelectorAll('.js-identify')
  for (var i = 0, il = identify_items.length; i < il; i++) {
    identify_items[i].addEventListener('click', onIdentifyClick, false)
  }

  var scan_items = document.querySelectorAll('.js-scan')
  for (var i = 0, il = scan_items.length; i < il; i++) {
    scan_items[i].addEventListener('click', onScanClick, false)
  }

  var navigation_items = document.querySelectorAll('.js-navigation')
  for (var i = 0, il = navigation_items.length; i < il; i++) {
    navigation_items[i].addEventListener('click', onNavigationClick, false)
  }

  var get_info_items = document.querySelectorAll('.js-get-info')
  for (var i = 0, il = get_info_items.length; i < il; i++) {
    get_info_items[i].addEventListener('click', onGetInfoClick, false)
  }

  show_play_next_list_parents()
}

init();
