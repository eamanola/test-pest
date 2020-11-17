var create_player = (function(w) {
  var document = w.document

  function request_transcoding() {
    var video = document.querySelector('video');
    var sources = document.querySelectorAll('source')
    var streams = []

    for (var i = 0, il = sources.length; i < il; i++) {
      var source = sources[i]
      var source_src = source.getAttribute("src")

      if (!/\/transcode$/.test(source_src)) {
        streams.push(source_src + "/transcode")
      }
      video.removeChild(source)
    }

    if (sources.length) {
      console.log('adding new sources')
      create_sources(video, streams)
    }
  }

  function create_sources(video, streams) {
    var error_count = 0
    var src = null
    for (var i = 0, il = streams.length; i < il; i ++) {
      src = document.createElement('source')
      //src.setAttribute("type", "video/webm")
      src.setAttribute("src", streams[i])
      src.addEventListener("error", function(e) {
        console.log(++error_count, e)
        if (error_count == video.querySelectorAll('source').length) {
          console.error('transcode required')
          request_transcoding()
        }
      }, false)

      video.appendChild(src)
    }
  }

  function option_to_track(option) {
    var track = document.createElement('track')
    track.setAttribute('src', option.value)
    track.setAttribute("label", option.innerHTML)
    track.setAttribute("kind", "subtitles")

    return track
  }

  var ass_renderer = null
  function create_subtitles(wrapper, controls, video, subtitles, fonts) {
    if (subtitles.length > 0) {
      var subtitle_select = document.createElement("select")
      controls.appendChild(subtitle_select)

      var none_option = document.createElement("option")
      none_option.value = ""
      none_option.innerHTML = "Off"
      subtitle_select.appendChild(none_option)

      subtitle_select.addEventListener("change", function() {
        var old_tracks = video.querySelectorAll("track")
        for (var i = 0, il = old_tracks.length; i < il; i ++) {
          video.removeChild(old_tracks[i])
        }

        if (ass_renderer !== null) {
          try {
            ass_renderer.freeTrack()
          } catch (e) {
            console.log('ass render', e)
          }
        }

        if (subtitle_select.value) {
          var selected_option = subtitle_select.querySelector(
            'option[value="' + subtitle_select.value + '"]'
          )

          var is_ass = /\.ass$/.test(subtitle.src)

          if (is_ass) {
            try {
              if (ass_renderer === null) {
                ass_renderer = new SubtitlesOctopus({
                  video: video,
                  subUrl: selected_option.value,
                  fonts: fonts,
                  workerUrl: '/scripts/octopus-ass/subtitles-octopus-worker.js',
                  legacyWorkerUrl: '/scripts/octopus-ass/subtitles-octopus-worker-legacy.js'
                })
              } else {
                ass_renderer.setTrackByUrl(selected_option.value)
              }
            } catch (e) {
              console.log('ass render', e)
            }
          } else {
            var track = option_to_track(selected_option)
            video.appendChild(track)
            video.textTracks[0].mode = "showing"
          }
        }
      }, false)

      var subtitle = null, label = null, subtitle_option = null
      for (var i = 0, il = subtitles.length; i < il; i ++) {
        subtitle_option = document.createElement("option")

        subtitle = subtitles[i]

        label = subtitle.lang + (subtitle.forced ? "(forced)" : "")
        subtitle_option.innerHTML = label
        // subtitle_option.setAttribute('data-lang', subtitle.lang)
        subtitle_option.value = subtitle.src

        if (subtitle.default === true) {
          subtitle_option.setAttribute("selected", "selected")

          var is_ass = /\.ass$/.test(subtitle.src)

          if (is_ass) {
            try {
              if (ass_renderer === null) {
                ass_renderer = new SubtitlesOctopus({
                  video: video,
                  subUrl: subtitle.src,
                  fonts: fonts,
                  workerUrl: '/scripts/octopus-ass/subtitles-octopus-worker.js',
                  legacyWorkerUrl: '/scripts/octopus-ass/subtitles-octopus-worker-legacy.js'
                })
              } else {
                ass_renderer.setTrackByUrl(subtitle.src)
              }
            } catch (e) {
              console.log('ass render', e)
            }
          } else {
            var track = option_to_track(subtitle_option)
            video.appendChild(track)
            video.textTracks[0].mode = "showing"
          }
        }

        subtitle_select.appendChild(subtitle_option)
      }

    }
  }

  function create_audio(wrapper, controls, video, audio_obj) {
    var audio_select = null, audio_option = null, current_audio = null
    if (audio_obj.length > 0) {
      audio_select = document.createElement('select')
      controls.appendChild(audio_select)

      current_audio = null
      video.addEventListener("play", function(){
        if (current_audio !== null) {
          setTimeout(function(){
            current_audio.currentTime = video.currentTime
            current_audio.play()
          }, 100)
        }
      }, false)

      video.addEventListener('timeupdate', function() {
        if (current_audio != null) {
          if (Math.abs(current_audio.currentTime - video.currentTime) > 0.5)
            current_audio.currentTime = video.currentTime
        }
      }, false)

      video.addEventListener("pause", function(){
        if (current_audio !== null) {
          current_audio.pause()
        }
      }, false)

      audio_select.addEventListener("change", function() {
        var current_volume = null
        if (current_audio !== null) {
          current_audio.pause()
          current_volume = current_audio.volume
        }
        else {
          current_volume = video.volume
        }
        if (this.value == "") {
          current_audio = null
          video.muted = false
          video.volume = current_volume
        } else {
          var audio_el = wrapper.querySelector(
            'audio[data-lang="' + this.value + '"]'
          )
          current_audio = audio_el
          video.muted = true
          current_audio.volume = current_volume

          if (!video.paused) {
            current_audio.play()
          }
        }
      }, false)

      audio_option = document.createElement('option')
      audio_option.innerHTML = "default"
      audio_option.setAttribute("value", "")
      audio_select.appendChild(audio_option)
    }

    var audio = null
    for (var i = 0, il = audio_obj.length; i < il; i++) {
      audio = document.createElement('audio')
      //audio.setAttribute("type", "audio/ogg")
      audio.setAttribute("src", audio_obj[i].src)
      audio.setAttribute("data-lang", audio_obj[i].lang)
      audio.setAttribute("controls", "1")
      audio.preload = "auto"
      audio.style.display = "none"
      wrapper.appendChild(audio);

      audio_option = document.createElement('option')
      audio_option.innerHTML = audio_obj[i].lang
      audio_option.setAttribute("value", audio_obj[i].lang)
      audio_select.appendChild(audio_option);
    }

    var overlay = wrapper.querySelector(".video-overlay")
    overlay.addEventListener("wheel", function(e) {
      var el = current_audio || video
      var new_volume = el.volume - (e.deltaY / 3 * 0.05)
      if (new_volume < 0) new_volume = 0
      else if (new_volume > 1)  new_volume = 1

      el.volume = new_volume
    }, false)
  }

  function close_player() {
    var wrapper = document.querySelector(".video-wrapper")
    var video = wrapper.querySelector("video")
    var audio = wrapper.querySelectorAll("audio")

    video.pause()
    console.log(video.currentTime)

    if (can_play_timeout) {
      clearTimeout(can_play_timeout)
      can_play_timeout = null
    }

    if (create_source_x_timeout) {
      clearTimeout(create_source_x_timeout)
      can_play_timeout = null
    }

    video.removeEventListener("canplay", onCanPlay, false)
    video.removeEventListener("ended", onVideoEnded, false)

    for (var i = 0, il = audio.length; i < il; i++) {
      audio[i].pause()
      audio[i].src = "foo"
      audio[i].load()
    }

    if (ass_renderer != null) {
      try {
        ass_renderer.dispose()
      } catch (e) {
        console.log('ass render', e)
      }
      ass_renderer = null
    }

    var sources = video.querySelectorAll("source")
    for (var i = 0, il = sources.length; i < il; i++) {
      video.removeChild(sources[i])
    }
    video.load()

    playing = null
    document.body.removeChild(wrapper)
  }

  var playing = null
  function onVideoEnded(e) {
    close_player()

    var els = document.querySelectorAll(
      '[data-id=' + playing + '] .js-played input'
    )
    for (var i = 0, il = els.length; i < il; i++) {
      //els[i].checked = true
      //w.onPlayedChange( { target: els[i] } )
    }
  }

  var can_play_timeout = null
  function onCanPlay(e) {
    var BUFFER_TIME = 1000 * 5 // 10s

    can_play_timeout = setTimeout(function() {
      var wrapper = document.querySelector(".video-wrapper")
      wrapper.className = "video-wrapper"

      var video = wrapper.querySelector("video")
      video.play()
    }, BUFFER_TIME)
  }

  function toggleFullscreen(e) {
    var wrapper = document.querySelector(".video-wrapper")
    var fullscreen_button = wrapper.querySelector(".fullscreen-button")

    if (document.fullscreen){
      document.exitFullscreen()

      fullscreen_button.innerHTML = "Fullscreen"
    } else {
      wrapper.requestFullscreen()

      fullscreen_button.innerHTML = "Exit Fullscreen"
    }
  }

  var hide_ui_timeout = null
  function restart_hide_ui_timeout(e) {
    if (hide_ui_timeout) {
      clearTimeout(hide_ui_timeout)
    }

    var controls = document.querySelector(".video-controls")
    controls.style.display = ""

    var overlay = document.querySelector(".video-overlay")
    overlay.style.cursor = ""

    start_hide_ui_timeout()
  }

  function start_hide_ui_timeout() {
    var HIDE_UI_TIMEOUT = 5 * 1000
    hide_UI_timeout = setTimeout(function() {
      var controls = document.querySelector(".video-controls")
      controls.style.display = "none"

      var overlay = document.querySelector(".video-overlay")
      overlay.style.cursor = "none"
    }, HIDE_UI_TIMEOUT)
  }

  function onFullscreenChange(e) {
    var overlay = document.querySelector(".video-overlay")

    if (document.fullscreen) {
      start_hide_ui_timeout()

      overlay.addEventListener(
        "mousemove", restart_hide_ui_timeout, false
      )
    } else {
      var controls = document.querySelector(".video-controls")
      if (controls)
        controls.style.display = ""

      if (overlay) {
        overlay.style.cursor = ""

        overlay.removeEventListener(
          "mousemove", restart_hide_ui_timeout, false
        )
      }
    }
  }

  function format_secs(secs) {
    var hours = Math.floor(secs/ 3600)
    var minutes = Math.floor((secs % 3600) / 60)
    var seconds = Math.floor(secs % 60)

    var time = ""
    if (hours > 0) {
      time += hours + ":"
    }

    time += (hours > 0 ? (minutes < 10 ? "0" : "") : "") + minutes + ":"
    time += (seconds < 10 ? "0" : "") + seconds

    return time
  }

  var create_source_x_timeout = null
  function create_player(streams_obj) {
    playing = streams_obj.id

    var wrapper = document.createElement('div')
    wrapper.className = "video-wrapper buffering"

    var controls = document.createElement('div')
    controls.className = "video-controls"
    wrapper.appendChild(controls)

    var close_button = document.createElement('button')
    close_button.addEventListener("click", close_player, false)
    close_button.innerHTML = "Close"
    controls.appendChild(close_button)

    var fullscreen_button = document.createElement('button')
    fullscreen_button.addEventListener("click", toggleFullscreen, false)
    fullscreen_button.className = "fullscreen-button"
    fullscreen_button.innerHTML = "Fullscreen"
    controls.appendChild(fullscreen_button)

    document.addEventListener("fullscreenchange", onFullscreenChange, false);

    var play_position = document.createElement("div")
    play_position.className = "video-position-wrapper"

    var play_position_total = document.createElement("div")
    play_position_total.className = "video-position-total"
    play_position_total.addEventListener("click", function(e) {
      var percent = (e.layerX / play_position_total.offsetWidth)
      if (percent < 0.025) percent = 0

      var new_time = percent * duration
      if (new_time > v.buffered.end(0)) new_time = v.buffered.end(0)

      v.currentTime = new_time
    }, false)
    play_position.appendChild(play_position_total)

    var play_position_buffered = document.createElement("div")
    play_position_buffered.className = "video-position-buffered"
    play_position_total.appendChild(play_position_buffered)

    var play_position_played = document.createElement("div")
    play_position_played.className = "video-position-played"
    play_position_total.appendChild(play_position_played)

    var play_position_time = document.createElement("span")
    play_position_time.innerHTML = "0:00"
    play_position.appendChild(play_position_time)

    if (streams_obj.duration) {
      var play_position_duration = document.createElement("span")
      play_position_duration.innerHTML = "/" + format_secs(streams_obj.duration)
      play_position.appendChild(play_position_duration)
    }

    controls.appendChild(play_position)

    var v = document.createElement('video')
    v.setAttribute("width", "640")
    // v.setAttribute("controls", "1")
    // v.muted = true
    v.autoplay = false
    v.preload = "auto"
    wrapper.appendChild(v)

    var loading = document.createElement('img');
    loading.setAttribute("src", "images/loading.gif")
    loading.className = "loading"
    wrapper.appendChild(loading)

    var overlay = document.createElement('div')
    overlay.className = "video-overlay"
    wrapper.appendChild(overlay)

    overlay.addEventListener("click", function(e) {
      e.preventDefault()
      e.stopPropagation()
      if (v.paused) {
        v.play()
      } else {
        v.pause()
      }
    }, false)

    overlay.addEventListener("dblclick", toggleFullscreen, false)

    v.addEventListener("error", function(e) {
      console.error(e)
    }, false)

    v.addEventListener("ended", onVideoEnded, false)

    v.addEventListener("progress", function() {
      if(duration) {
        if (v.buffered.length) {
          play_position_buffered.style.width =
          (Math.min(v.buffered.end(0) / duration, 1) * 100) + '%'
        }
      }
    }, false)

    var duration = streams_obj.duration
    v.addEventListener("timeupdate", function() {
      var time = format_secs(v.currentTime)
      play_position_time.innerHTML = time

      if(duration) {
        play_position_played.style.width =
          (Math.min(v.currentTime / duration, 1) * 100) + '%'
      }
    }, false)

    create_sources(v, streams_obj.streams)
    create_subtitles(
      wrapper, controls, v, streams_obj.subtitles, streams_obj.fonts
    )
    create_audio(wrapper, controls, v, streams_obj.audio)

    v.addEventListener("canplay", onCanPlay, false)

    document.body.prepend(wrapper)
  }

  return create_player
})(window)
