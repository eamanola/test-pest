var create_player = (function() {
  function format_secs(secs) {
    var hours = Math.floor(secs/ 3600)
    var minutes = Math.floor((secs % 3600) / 60)
    var seconds = Math.floor(secs % 60)

    var time = ""
    time += (hours > 0) ? (hours + ":") : ""
    time += (hours > 0 ? (minutes < 10 ? "0" : "") : "") + minutes + ":"
    time += (seconds < 10 ? "0" : "") + seconds

    return time
  }

  var Player = function(streams_obj) {
    this.media_id = streams_obj.id
    this.duration = streams_obj.duration

    var wrapper = this.wrapper = this.create_wrapper()
    this.set_state("buffering")

    wrapper.appendChild(this.create_video())
    wrapper.appendChild(this.create_loading())
    wrapper.appendChild(this.create_overlay())
    var controls = this.create_controls()

    if (streams_obj.audio.length > 0) {
      this.create_audio(streams_obj.audio)
      controls.appendChild(this.create_audio_select(streams_obj.audio))
      this.sync_audio()
    }

    if (streams_obj.subtitles.length > 0) {
      this.fonts = streams_obj.fonts
      controls.appendChild(this.create_subtitle_select(streams_obj.subtitles))
    }

    controls.appendChild(this.create_close_btn())
    controls.appendChild(this.create_fullscreen_btn())
    controls.appendChild(this.create_play_position())
    wrapper.appendChild(controls)

    this.create_sources(streams_obj.streams)

    document.addEventListener(
      "fullscreenchange",
      this.on_fullscreen_changed.bind(this),
      false
    );

    document.body.prepend(wrapper)
  }

  Player.prototype = {
    media_id: null,
    duration: 0,
    wrapper : null,
    current_audio: null,
    ass_renderer: null,
    BUFFER_TIME: 1000 * 5,
    fullscreen_hide_ui_timeout: null,
    FULLSCREEN_HIDE_UI_TIMEOUT: 5 * 1000,
    create_wrapper: function() {
      var wrapper = document.createElement('div')
      wrapper.className = "video-wrapper"

      return wrapper
    },
    set_state: function(state) {
      if (state == "buffering")
        this.wrapper.className += " buffering"
      else if (state == "playing")
        this.wrapper.className =
          this.wrapper.className.replace(" buffering", "")

    },
    video: function() {
      return this.wrapper.querySelector("video")
    },
    controls: function() {
      return this.wrapper.querySelector(".video-controls")
    },
    overlay: function() {
      return this.wrapper.querySelector(".video-overlay")
    },
    play_position_played: function() {
      return this.wrapper.querySelector(".video-position-played")
    },
    play_position_buffered: function() {
      return this.wrapper.querySelector(".video-position-buffered")
    },
    play_position_time: function() {
      return this.wrapper.querySelector(".video-position-time")
    },

    create_video: function() {
      var video = document.createElement('video')
      //v.setAttribute("width", "640")
      // v.setAttribute("controls", "1")
      // v.muted = true
      video.autoplay = false
      video.preload = "auto"

      video.addEventListener("error", console.error, false)

      // ? check effect tonight
      video.addEventListener("ended", this.close.bind(this), false)

      var player = this
      video.addEventListener("progress", function() {
        var duration = player.duration
        if(duration) {
          if (this.buffered.length) {
            player.play_position_buffered().style.width =
              this.buffered.end(0) / duration * 100 + '%'
          }
        }
      }, false)

      video.addEventListener("timeupdate", function() {
        var time = format_secs(this.currentTime)
        player.play_position_time().innerHTML = time

        var duration = player.duration
        if(duration) {
          player.play_position_played().style.width =
            this.currentTime / duration * 100 + '%'
        }
      }, false)

      video.addEventListener("canplay", function(e) {
        this.BUFFER_TIME

        setTimeout(function() {
          this.set_state("playing")

          this.video().play()

          setTimeout(function() {
            if (this.video().videoHeight === 0) {
              this.show_chrome_transcode()
            }
          }.bind(this), 1000)
        }.bind(this), this.BUFFER_TIME)
      }.bind(this), false)

      return video
    },
    create_loading: function() {
      var loading = document.createElement('img');
      loading.setAttribute("src", "images/loading.gif")
      loading.className = "loading"

      return loading
    },
    create_overlay: function() {
      var overlay = document.createElement('div')
      overlay.className = "video-overlay"

      overlay.addEventListener("click", function(e) {
        e.preventDefault()
        e.stopPropagation()
        var video = this.video()
        if (video.paused) {
          video.play()
        } else {
          video.pause()
        }
      }.bind(this), false)

      overlay.addEventListener(
        "dblclick",
        this.toggleFullscreen.bind(this),
        false
      )

      overlay.addEventListener("wheel", function(e) {
        var el = this.current_audio || this.video()
        var new_volume = el.volume - (e.deltaY / 3 * 0.05)
        if (new_volume < 0) new_volume = 0
        else if (new_volume > 1)  new_volume = 1

        el.volume = new_volume
      }.bind(this), false)

      return overlay
    },
    create_controls: function() {
      var controls = document.createElement('div')
      controls.className = "video-controls"

      return controls
    },
    create_close_btn: function() {
      var close_button = document.createElement('button')
      close_button.addEventListener("click", this.close.bind(this), false)
      close_button.innerHTML = "Close"

      return close_button
    },
    create_fullscreen_btn: function() {
      var fullscreen_button = document.createElement('button')
      fullscreen_button.addEventListener(
        "click",
        this.toggleFullscreen.bind(this),
        false
      )
      fullscreen_button.className = "fullscreen-button"
      fullscreen_button.innerHTML = "Fullscreen"

      return fullscreen_button
    },
    create_play_position : function() {
      var play_position = document.createElement("div")
      play_position.className = "video-position-wrapper"

      play_position.appendChild(this.create_play_position_total())

      play_position.appendChild(this.create_play_position_time())

      if (this.duration) {
        play_position.appendChild(this.create_play_position_duration())
      }

      return play_position
    },
    create_play_position_total: function() {
      var play_position_total = document.createElement("div")
      play_position_total.className = "video-position-total"
      play_position_total.addEventListener("click", function(e) {
        var video = this.video()
        var duration = this.duration

        var percent = (e.layerX / play_position_total.offsetWidth)
        if (percent < 0.025) percent = 0

        var new_time = percent * duration
        var buffered_end = video.buffered.end(0)
        if (new_time > buffered_end)
          new_time = buffered_end

        video.currentTime = new_time
      }.bind(this), false)

      play_position_total.appendChild(this.create_play_position_buffered())
      play_position_total.appendChild(this.create_play_position_played())

      return play_position_total
    },
    create_play_position_buffered: function() {
      var play_position_buffered = document.createElement("div")
      play_position_buffered.className = "video-position-buffered"

      return play_position_buffered
    },
    create_play_position_played: function() {
      var play_position_played = document.createElement("div")
      play_position_played.className = "video-position-played"

      return play_position_played
    },
    create_play_position_time: function() {
      var play_position_time = document.createElement("span")
      play_position_time.className = "video-position-time"
      play_position_time.innerHTML = "0:00"

      return play_position_time
    },
    create_play_position_duration: function() {
      var play_position_duration = document.createElement("span")
      play_position_duration.innerHTML = "/" + format_secs(this.duration)

      return play_position_duration
    },
    create_audio_select: function(audio_obj) {
      var audio_select = document.createElement('select')

      audio_select.addEventListener("change", function() {
        var current_audio = this.current_audio
        var video = this.video()
        var current_volume = null
        if (current_audio !== null) {
          current_audio.pause()
          current_volume = current_audio.volume
        }
        else {
          current_volume = video.volume
        }
        if (audio_select.value == "") {
          video.muted = false
          video.volume = current_volume
          this.current_audio = null
        } else {
          var audio_el = this.wrapper.querySelector(
            'audio[data-lang="' + audio_select.value + '"]'
          )
          video.muted = true
          audio_el.volume = current_volume
          if (!video.paused) {
            audio_el.play()
          }
          this.current_audio = audio_el
        }
      }.bind(this), false)

      var audio_option = document.createElement('option')
      audio_option.innerHTML = "default"
      audio_option.setAttribute("value", "")
      audio_select.appendChild(audio_option)

      for (var i = 0, il = audio_obj.length; i < il; i++) {
        audio_option = document.createElement('option')
        audio_option.innerHTML = audio_obj[i].lang
        audio_option.setAttribute("value", audio_obj[i].lang)
        audio_select.appendChild(audio_option);
      }

      return audio_select
    },
    create_subtitle_select: function(subtitles) {
      var subtitle_select = document.createElement("select")

      subtitle_select.addEventListener("change", function() {
        var video = this.video()
        var old_tracks = video.querySelectorAll("track")
        for (var i = 0, il = old_tracks.length; i < il; i ++) {
          video.removeChild(old_tracks[i])
        }

        if (this.ass_renderer !== null) {
          try {
            this.ass_renderer.freeTrack()
          } catch (e) {
            console.log('ass render', e)
          }
        }

        this.set_subtitle(subtitle_select.value)
      }.bind(this), false)

      var subtitle_option = document.createElement("option")
      subtitle_option.value = ""
      subtitle_option.innerHTML = "Off"
      subtitle_select.appendChild(subtitle_option)

      var subtitle = null, label = null, subtitle_option = null
      for (var i = 0, il = subtitles.length; i < il; i ++) {
        subtitle = subtitles[i]
        label = subtitle.lang + (subtitle.forced ? "(forced)" : "")

        subtitle_option = document.createElement("option")
        subtitle_option.innerHTML = label
        // subtitle_option.setAttribute('data-lang', subtitle.lang)
        subtitle_option.value = subtitle.src

        if (subtitle.default === true) {
          subtitle_option.setAttribute("selected", "selected")

          this.set_subtitle(subtitle.src)
        }

        subtitle_select.appendChild(subtitle_option)
      }

      return subtitle_select
    },

    create_sources: function(streams) {
      var video = this.video()
      var error_count = 0
      var src = null
      for (var i = 0, il = streams.length; i < il; i ++) {
        src = document.createElement('source')
        //src.setAttribute("type", "video/webm")
        src.setAttribute("src", streams[i])
        src.addEventListener("error", function(e) {
          console.log(++error_count, e)
          if (error_count == video.querySelectorAll('source').length) {
            console.log('transcode required')
            this.request_transcoding()
          }
        }.bind(this), false)

        video.appendChild(src)
      }
    },
    create_audio: function(audio_obj) {
      var audio = null
      for (var i = 0, il = audio_obj.length; i < il; i++) {
        audio = document.createElement('audio')
        // audio.setAttribute("type", "audio/ogg")
        audio.setAttribute("src", audio_obj[i].src)
        audio.setAttribute("data-lang", audio_obj[i].lang)
        // audio.setAttribute("controls", "1")
        audio.preload = "auto"
        audio.style.display = "none"
        this.wrapper.appendChild(audio);
      }
    },

    sync_audio: function() {
      var video = this.video()

      video.addEventListener("play", function() {
        var current_audio = this.current_audio
        var video = this.video()
        if (current_audio !== null) {
          setTimeout(function() {
            current_audio.currentTime = video.currentTime
            current_audio.play()
          }, 100)
        }
      }.bind(this), false)

      video.addEventListener('timeupdate', function() {
        var current_audio = this.current_audio
        var video = this.video()
        if (current_audio != null) {
          if (Math.abs(current_audio.currentTime - video.currentTime) > 0.5)
            current_audio.currentTime = video.currentTime
        }
      }.bind(this), false)

      video.addEventListener("pause", function() {
        var current_audio = this.current_audio
        if (current_audio !== null) {
          current_audio.pause()
        }
      }.bind(this), false)
    },
    set_subtitle: function(src) {
      var is_ass = /\.ass$/.test(src)

      if (is_ass) {
        try {
          if (this.ass_renderer === null) {
            this.ass_renderer = new SubtitlesOctopus({
              video: this.video(),
              subUrl: src,
              fonts: this.fonts,
              workerUrl: '/scripts/octopus-ass/subtitles-octopus-worker.js',
              legacyWorkerUrl: '/scripts/octopus-ass/subtitles-octopus-worker-legacy.js'
            })
          } else {
            this.ass_renderer.setTrackByUrl(src)
          }
        } catch (e) {
          console.log('ass render', e)
        }
      } else {
        var track = document.createElement('track')
        track.setAttribute('src', src)
        track.setAttribute("kind", "subtitles")

        var video = this.video()
        video.appendChild(track)
        video.textTracks[0].mode = "showing"
      }
    },
    toggleFullscreen: function(e) {
      var fullscreen_button = this.wrapper.querySelector(".fullscreen-button")

      if (document.fullscreen){
        document.exitFullscreen()

        fullscreen_button.innerHTML = "Fullscreen"
      } else {
        this.wrapper.requestFullscreen().then(function(){
          fullscreen_button.innerHTML = "Exit Fullscreen"
        })
      }
    },
    show_chrome_transcode: function() {
      var chrome_transcode = document.createElement("div")
      chrome_transcode.className = "chrome-transcode"

      var chrome_transcode_msg = document.createElement("span")
      chrome_transcode_msg.innerHTML = "Hearing sound, but no video on Chrome?"
      chrome_transcode.appendChild(chrome_transcode_msg)

      var chrome_transcode_btn = document.createElement("button")
      chrome_transcode_btn.innerHTML = "Click here"
      chrome_transcode_btn.addEventListener('click', function() {
          this.wrapper.removeChild(chrome_transcode)
          this.set_state("buffering")
          this.request_transcoding()
      }.bind(this), false)
      chrome_transcode.appendChild(chrome_transcode_btn)

      this.wrapper.appendChild(chrome_transcode)
    },
    close: function() {
      var video = this.wrapper.querySelector("video")
      video.pause()
      console.log(video.currentTime)

      var duration = this.duration
      if (duration) {
        if (video.currentTime / duration > 0.9) {
          console.log('video marked played')

          var els = document.querySelectorAll(
            '[data-id="' + this.media_id + '"] .js-played input'
          )
          for (var i = 0, il = els.length; i < il; i++) {
            els[i].checked = true
            window.onPlayedChange( { target: els[i] } )
          }
        }
      }

      var audio = this.wrapper.querySelectorAll("audio")
      for (var i = 0, il = audio.length; i < il; i++) {
        audio[i].pause()
        audio[i].src = "fail-load"
        audio[i].load()
      }

      if (this.ass_renderer != null) {
        try {
          this.ass_renderer.dispose()
        } catch (e) {
          console.log('ass render', e)
        }
        this.ass_renderer = null
      }

      var sources = video.querySelectorAll("source")
      for (var i = 0, il = sources.length; i < il; i++) {
        video.removeChild(sources[i])
      }
      video.load()

      document.body.removeChild(this.wrapper)
    },
    request_transcoding: function() {
      var video = this.video()
      var sources = video.querySelectorAll('source')
      var streams = []

      var source = source_src = null
      for (var i = 0, il = sources.length; i < il; i++) {
        source = sources[i]
        source_src = source.getAttribute("src")

        if (!/\/transcode$/.test(source_src)) {
          streams.push(source_src + "/transcode")
        }
        video.removeChild(source)
      }

      if (sources.length) {
        console.log('adding new sources')
        this.create_sources(streams)
        video.load()
      }
    },

    fullscreen_hide_ui: function() {
      if (document.fullscreen) {
        var controls = this.controls()
        if (controls)
          controls.style.display = "none"

        var overlay = this.overlay()
        if (overlay)
          overlay.style.cursor = "none"
      }
    },
    fullscreen_show_ui: function() {
      this.controls().style.display = ""

      this.overlay().style.cursor = ""
    },
    restart_fullscreen_hide_ui_timeout: function() {
      this.fullscreen_show_ui()

      if (this.fullscreen_hide_ui_timeout) {
        clearTimeout(this.fullscreen_hide_ui_timeout)
      }

      this.fullscreen_hide_ui_timeout = setTimeout(
        this.fullscreen_hide_ui.bind(this),
        this.FULLSCREEN_HIDE_UI_TIMEOUT
      )
    },
    on_fullscreen_changed: function(e) {
      var overlay = this.overlay()

      if (document.fullscreen) {
        this.restart_fullscreen_hide_ui_timeout()

        overlay.addEventListener(
          "mousemove",
          this.restart_fullscreen_hide_ui_timeout.bind(this),
          false
        )
      } else {
        var controls = this.controls()
        if (controls)
          controls.style.display = ""

        if (overlay) {
          overlay.style.cursor = ""

          overlay.removeEventListener(
            "mousemove",
            this.restart_fullscreen_hide_ui_timeout.bind(this),
            false
          )
        }
      }
    }
  }

  return function (streams_obj) {
    new Player(streams_obj)
  }
})()
