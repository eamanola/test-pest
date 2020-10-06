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
  type = null
  data_id = null

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
  url = "/" + window.location.search
  ajax(
    url,
    function updatePageDataReceived(responseText) {
      document.body.innerHTML = responseText

      init()
    }
  )
}

function onNavigationClick(e) {
  id_obj = get_data_id(e.target)
  type = id_obj.type
  data_id = id_obj.data_id

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
}

function onScanCompleted(responseText) {
  return updatePage();

  response = JSON.parse(responseText)
  console.log(response)

  data_id = response.data_id
  query = '[data-id="' + data_id + '"] .js-scan'
  var el = document.querySelectorAll(query)[0]
  el.innerHTML = "Scan"
  el.addEventListener('click', onScanClick, false)
}

function onScanClick(e) {
  id_obj = get_data_id(e.target)
  data_id = id_obj.data_id
  if (data_id) {
    ajax('/?s=' + data_id, onScanCompleted)

    query = '[data-id="' + data_id + '"] .js-scan'
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
  id_obj = get_data_id(e.target)
  data_id = id_obj.data_id
  if (data_id) {
    ajax('/?i=' + data_id, onIdentifyCompleted)

    query = '[data-id="' + data_id + '"] .js-identify'
    var el = document.querySelectorAll(query)[0]
    el.innerHTML = "identifying"
    el.removeEventListener('click', onIdentifyClick, false)
  }

  return false
}

function init() {
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
}

init();