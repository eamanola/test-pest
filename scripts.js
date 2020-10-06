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
    if(el.classList.contains('js-container'))
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

function onScanCompleted(responseText) {
  return updatePage();

  var response = JSON.parse(responseText)
  console.log(response)

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

function onIdentifyCompleted(responseText) {
  return updatePage();
  console.log(responseText)
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

function onToggleToPlayClick(e) {
  e.preventDefault();

  var id_obj = get_data_id(e.target)
  var data_id = id_obj.data_id

  if (data_id) {
    var list_str = storage.getItem('add-to-play-list')
    var list = list_str ? list_str.split(",") : []
    var title = ""

    var index = list.indexOf(data_id)
    if (index === -1) {
      list.push(data_id)
      title = "-Play"
    } else {
      list.splice(index, 1)
      title = "+Play"
    }

    storage.setItem('add-to-play-list', list.join(","))

    update_play()

    var query = '[data-id="' + data_id + '"] .js-add-to-play'
    var el = document.querySelectorAll(query)[0]
    el.innerHTML = title
  }

  return false
}

function onPlayConfirmed(responseText) {
  console.log(responseText)
}

function play(e) {
  if (e && e.preventDefault)
    e.preventDefault();

  var list_str = storage.getItem('add-to-play-list')
  if (list_str) {
    ajax('/?p=' + list_str, onPlayConfirmed)
  }

  return false
}

function onPlayedSaved(responseText) {
  console.log(responseText);
}

function onPlayedClick(e) {
  e.preventDefault();

  var id_obj = get_data_id(e.target)
  var data_id = id_obj.data_id

  if (data_id) {
    var url = ["/?", e.target.checked ? "pa" : "pr", "=", data_id].join("")
    ajax(url, onPlayedSaved)
  }

  return false
}

function update_play() {
  var list_str = storage.getItem('add-to-play-list')
  var list = list_str ? list_str.split(",") : []
  document.querySelectorAll('.js-play')[0]
    .innerHTML = "Play(" + list.length + ")"
}

function onClearPlayClick(e) {
  e.preventDefault();

  storage.removeItem('add-to-play-list')
  update_play()
  var add_to_play_items = document.querySelectorAll('.js-add-to-play')
  for (var i = 0, il = add_to_play_items.length; i < il; i++)
    if (add_to_play_items[i].innerHTML !== "+Play") {
      add_to_play_items[i].innerHTML = "+Play"
    }

  return false
}

function update_add_to_play_items() {
  var add_to_play_items = document.querySelectorAll('.js-add-to-play')

  var list_str = storage.getItem('add-to-play-list')
  var list = list_str ? list_str.split(",") : null
  var data_id = id_obj = null

  for (var i = 0, il = add_to_play_items.length; i < il; i++) {
    if (list) {
      id_obj = get_data_id(add_to_play_items[i])
      data_id = id_obj.data_id

      if (data_id && list.indexOf(data_id) !== -1) {
        add_to_play_items[i].innerHTML = "-Play"
      } else {
        add_to_play_items[i].innerHTML = "+Play"
      }
    }
  }
}

function init() {
  var play_item = document.querySelectorAll('.js-play')[0]
  play_item.addEventListener('click', play, false)

  var clear_play_item = document.querySelectorAll('.js-clear-play')[0]
  clear_play_item.addEventListener('click', onClearPlayClick, false)

  var played_items = document.querySelectorAll('.js-played')
  for (var i = 0, il = played_items.length; i < il; i++) {
    played_items[i].addEventListener('click', onPlayedClick, false)
  }

  var add_to_play_items = document.querySelectorAll('.js-add-to-play')
  for (var i = 0, il = add_to_play_items.length; i < il; i++) {
    add_to_play_items[i].addEventListener('click', onToggleToPlayClick, false)
  }
  update_add_to_play_items()

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

  update_play()
}

init();
