(function keyboard_interaction() {
  var hoverable = ['.media.line', '.container.line']

  function set_hover(el) {
    var previous_hover = document.querySelector('.hover')
    if (previous_hover){
      previous_hover.className =
        previous_hover.className.replace(/\s*hover/, '')
    }

    el.className = [el.className, "hover"].join(" ")
    el.scrollIntoView({ behavior: "smooth", block: "nearest" })
  }


  function index_of(hover, hoverables) {
    for (var i = 0, il = hoverables.length; i < il; i++) {
      if (hoverables[i] === hover) {
        return i
      }
    }

    return -1;
  }

  function items_per_line(item) {
    var style = window.getComputedStyle(item)
    var ipl = item.parentNode.offsetWidth /
    ( item.offsetWidth
      + parseInt(style.marginLeft, 10)
      + parseInt(style.marginRight, 10)
    )

    return Math.floor(ipl)
  }

  function onEnterClicked(el) {
    var id_obj = get_data_id(el)
    var type = id_obj.type
    var data_id = id_obj.data_id

    if (type && data_id) {
      if (type == "container") {
        getContainer(data_id, true)
      } else if (type == "media") {
        onPlaySingleClick({target:el})
      }
    }

    return false
  }

  function video_handler(e) {
    e.preventDefault()
    e.stopPropagation()
    if (e.keyCode == 415) { //remote play
      var video = document.querySelector("video")
      if (video) {
        video.play()
      }
    } else if (e.keyCode == 19) { //remote pause
      var video = document.querySelector("video")
      if (video) {
        video.pause()
      }
    } else if (e.keyCode == 413) { //remote stop
      // if (window._player) {
      //  window._player.close()
      //}
      if (player_is_open()) {
        history.go(-1)
      }
    } else if (e.keyCode == 460 || e.keyCode == 404) {  //remote subtitle | green
      var subtitle_select = window._player.subtitle_select()
      if (subtitle_select) {
        var s_options = subtitle_select.querySelectorAll("option")

        var next = subtitle_select.selectedIndex + 1
        if (next == s_options.length) next = 0

        subtitle_select.selectedIndex = next
        window._player.set_subtitle(subtitle_select.value)
      }
    } else if (e.keyCode == 403) {  //remote red
      var audio_select = window._player.audio_select()
      if (audio_select) {
        var a_options = audio_select.querySelectorAll("option")

        var next = audio_select.selectedIndex + 1
        if (next == a_options.length) next = 0

        audio_select.selectedIndex = next
        window._player.set_audio(audio_select.value)
      }
    }
  }

  window.addEventListener("keydown", function(e) {
    var add_media_lib_path = document.getElementById("add-media-library-path")
    if (e.target == add_media_lib_path) {
        return true
    }
    var next_item = null
    var hoverables = document.querySelectorAll(hoverable.join(","))

    var hover = document.querySelector('.hover')
    if (hover === null) {
      e.preventDefault()
      e.stopPropagation()

      if (hoverables.length){
        set_hover(hoverables[0])
      }
      return
    }

    if (player_is_open()) {
      return video_handler(e)
    }
    console.log(e.key, e.keyCode);

    var index = index_of(hover, hoverables)

    if (e.key === "ArrowLeft") {
      if (!next_item && (index > 0)) {
        next_item = hoverables[index - 1]
      }
    } else if (e.key === "ArrowRight") {
      if (!next_item && (index < hoverables.length - 1)) {
        next_item = hoverables[index + 1]
      }
    } else if (e.key === "ArrowUp") {
      var siblings = hover.parentNode.querySelectorAll(hoverable.join(","))
      var sib_index = index_of(hover, siblings)
      var ipl = items_per_line(hover)

      if (!next_item && (sib_index + 1 > ipl)) {
        next_item = siblings[sib_index - ipl]
      }

      if (!next_item && (index - sib_index > 0)) {
        next_item = hoverables[index - sib_index - 1]
      }

      if (!next_item) {
        e.preventDefault()
        e.stopPropagation()

        set_hover(hoverables[0])
        document.body.scrollIntoView({ behavior: "smooth" })
        return
      }
    } else if (e.key === "ArrowDown") {
      var siblings = hover.parentNode.querySelectorAll(hoverable.join(","))
      var sib_index = index_of(hover, siblings)
      var ipl = items_per_line(hover)

      if (!next_item && (sib_index + ipl < siblings.length - 1)) {
        next_item = siblings[sib_index + ipl]
      }

      if (!next_item && (sib_index < siblings.length - 1)) {
        var current_line = Math.floor(sib_index / ipl)
        var total_lines = Math.floor((siblings.length - 1) / ipl)
        if (current_line < total_lines) {
          next_item = siblings[siblings.length - 1]
        }
      }

      if (!next_item &&
        (index + (siblings.length - 1 - sib_index) < hoverables.length)) {

        next_item = hoverables[index + (siblings.length - 1 - sib_index) + 1]
      }
    } else if (e.key === "Enter") {
      e.preventDefault();
      e.stopPropagation();

      onEnterClicked(hover)
    } else if (e.keyCode == 403) { // remote red
      e.preventDefault();
      e.stopPropagation();

      toggle_played(get_data_id(hover).data_id)
    }

    if (next_item) {
      e.preventDefault()
      e.stopPropagation()
      set_hover(next_item)
    }
    // console.log(e)
  }, false)
})()
