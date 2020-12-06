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

  var Player = function(streams_url) {
    var wrapper = this.wrapper = this.create_wrapper()
    this.set_state("buffering")

    wrapper.appendChild(this.create_video())
    wrapper.appendChild(this.create_loading())
    wrapper.appendChild(this.create_overlay())

    var controls = this.create_controls()
    controls.appendChild(this.create_close_btn())
    controls.appendChild(this.create_fullscreen_btn())
    wrapper.appendChild(controls)

    document.addEventListener(
      "fullscreenchange",
      this.on_fullscreen_changed.bind(this),
      false
    );

    document.body.prepend(wrapper)

    ajax(
      streams_url,
      this.on_meta.bind(this)
    )
  }

  Player.prototype = {
    media_id: null,
    duration: 0,
    wrapper : null,
    current_audio: null,
    ass_renderer: null,
    BUFFER_TIME: 1000 * 2,
    fullscreen_hide_ui_timeout: null,
    FULLSCREEN_HIDE_UI_TIMEOUT: 5 * 1000,
    ENABLE_SEEK: true,
    start_time: 0,
    _can_play: [],
    create_wrapper: function() {
      var wrapper = document.createElement('div')
      wrapper.className = "video-wrapper"

      return wrapper
    },
    on_meta: function(responseText) {
      console.log(responseText)
      var streams_obj = JSON.parse(responseText);

      this.media_id = streams_obj.id
      this.duration = streams_obj.duration
      this.start_time = streams_obj.start_time

      this.create_sources(streams_obj.streams)

      if (streams_obj.audio.length > 0) {
        this.create_audio(streams_obj.audio)
        if (streams_obj.audio.length > 1) {
          this.controls()
            .appendChild(this.create_audio_select(streams_obj.audio))
        }
        this.sync_audio()
      }

      // create after sources, in case default subtitle requires re-transcoding
      if (streams_obj.subtitles.length > 0) {
        this.fonts = streams_obj.fonts
        this.controls()
          .appendChild(this.create_subtitle_select(streams_obj.subtitles))
      }

      this.controls().appendChild(this.create_play_position())
    },
    set_state: function(state) {
      if (state == "buffering")
        this.wrapper.className += " buffering"
      else if (state == "playing")
        this.wrapper.className =
          this.wrapper.className.replace(/\sbuffering/g, "")

    },
    current_time: function() {
      return this.video().currentTime + this.start_time
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
      video.muted = true

      video.addEventListener("error", console.error, false)

      // ? check effect tonight
      video.addEventListener("ended", this.close.bind(this), false)

      var player = this
      video.addEventListener("progress", function() {
        var duration = player.duration
        if(duration) {
          setTimeout(function(){
            if (video.buffered.length) {
              var buffered_end = video.buffered.end(0)

              if (player.current_audio) {
                if (player.current_audio.buffered.length) {
                  var audio_buffered_end = player.current_audio.buffered.end(0)
                  buffered_end = Math.min(buffered_end, audio_buffered_end)
                }
              }

              player.play_position_buffered().style.width =
                Math.floor(player.start_time + buffered_end)
                / duration * 100 + '%'
            }
          }, 1000)
        }
      }, false)

      video.addEventListener("timeupdate", function() {
        var time = format_secs(this.current_time())
        this.play_position_time().innerHTML = time

        var duration = this.duration
        if(duration) {
          setTimeout(function(){
            this.play_position_played().style.width =
              this.current_time() / duration * 100 + '%'
          }.bind(this), 0)
        }
      }.bind(this), false)

      this._can_play.push(video)
      video.addEventListener("canplay", this.on_can_play.bind(this), false)

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
          video.play().catch(this.on_video_play_error.bind(this))
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
        e.preventDefault()
        e.stopPropagation()
        var current_audio = this.current_audio
        if (current_audio) {
          var new_volume = current_audio.volume - (e.deltaY / 3 * 0.05)
          if (new_volume < 0) new_volume = 0
          else if (new_volume > 1)  new_volume = 1

          current_audio.volume = new_volume
        }
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

      if (this.duration){
        play_position.appendChild(this.create_play_position_duration())
      }

      return play_position
    },
    create_play_position_total: function() {
      var play_position_total = document.createElement("div")
      play_position_total.className = "video-position-total"

      if (this.ENABLE_SEEK)
      play_position_total.addEventListener("click", function(e) {
        var video = this.video()
        var current_audio = this.current_audio
        var duration = this.duration

        var percent = (e.layerX / play_position_total.offsetWidth)
        if (percent < 0.025) percent = 0

        var new_time = percent * duration - this.start_time

        var buffered_end = 0
        if (video.buffered.length)
          buffered_end = video.buffered.end(
            video.buffered.length - 1
          )

        if (current_audio) {
          if (current_audio.buffered.length) {
            var audio_buffered_end = current_audio.buffered.end(
              current_audio.buffered.length - 1
            );
            buffered_end = Math.min(buffered_end, audio_buffered_end)
          }
        }

        if (new_time > buffered_end)
          new_time = buffered_end
        else if (new_time < 0)
          new_time = 0

        video.currentTime = new_time
      }.bind(this), false)

      play_position_total.appendChild(this.create_play_position_buffered())
      play_position_total.appendChild(this.create_play_position_played())

      return play_position_total
    },
    create_play_position_buffered: function() {
      var play_position_buffered = document.createElement("div")
      play_position_buffered.className = "video-position-buffered"

      if(this.duration) {
        play_position_buffered.style.width =
            this.start_time / this.duration * 100 + '%'
      }

      return play_position_buffered
    },
    create_play_position_played: function() {
      var play_position_played = document.createElement("div")
      play_position_played.className = "video-position-played"

      if(this.duration) {
        play_position_played.style.width =
          this.start_time / this.duration * 100 + '%'
      }

      return play_position_played
    },
    create_play_position_time: function() {
      var play_position_time = document.createElement("span")
      play_position_time.className = "video-position-time"
      play_position_time.innerHTML = format_secs(this.start_time)

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
        this.set_audio(audio_select.value)
      }.bind(this), false)

      for (var i = 0, il = audio_obj.length; i < il; i++) {
        audio_option = document.createElement('option')
        audio_option.setAttribute("value", audio_obj[i].id)
        audio_option.innerHTML = (audio_obj[i].lang || "Unknown")
          + (audio_obj[i].forced ? " (forced)" : "")
          + (audio_obj[i].default ? " (default)" : "")

        if (audio_obj[i].default === true) {
          audio_option.setAttribute("selected", "selected")
        }

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

        var hardcoded_sub = /si=\d+$/.test(video.currentSrc)
        if (hardcoded_sub) {
          var new_sub_needs_hard_code = /\.tra$/.test(subtitle_select.value)
          if (!new_sub_needs_hard_code) {
              // remove old hard code
              this.request_transcoding()
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
        label = (subtitle.lang || "Unknown")
          + (subtitle.forced ? " (forced)" : "")
          + (subtitle.requires_transcode ? " (T)" : "")

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
          error_count = error_count + 1
          var source_length = video.querySelectorAll('source').length
          console.log(error_count + '/' + source_length, e)
          if (error_count == source_length) {
            this.request_transcoding()
          }
        }.bind(this), false)

        video.appendChild(src)
      }
    },
    create_audio: function(audio_obj) {
      var audio = null, source = null
      for (var i = 0, il = audio_obj.length; i < il; i++) {
        audio = document.createElement('audio')
        // audio.setAttribute("type", "audio/ogg")
        audio.setAttribute("data-audio-id", audio_obj[i].id)
        // audio.setAttribute("controls", "1")
        audio.preload = "auto"
        audio.autoplay = false
        audio.style.display = "none"

        for (var j = 0, jl = audio_obj[i].src.length; j < jl; j++) {
          source = document.createElement("source")
          source.setAttribute("src", audio_obj[i].src[j])
          source.addEventListener("error", console.error, false)
          audio.appendChild(source)
        }

        this.wrapper.appendChild(audio);

        if (audio_obj[i].default === true) {
          this.set_audio(audio_obj[i].id)
        }
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
            current_audio.play().catch(
              (function(audio) {
                return function(error) {
                  this.on_audio_play_error(error, audio)
                }
              })(current_audio).bind(this)
            )
          }.bind(this), 100)
        }
      }.bind(this), false)

      video.addEventListener('timeupdate', function() {
        var current_audio = this.current_audio
        var video = this.video()
        if (current_audio != null) {
          var time_diff = video.currentTime - current_audio.currentTime
          var out_of_sync = Math.abs(time_diff) > 0.5

          if (out_of_sync) {
            current_audio.currentTime = video.currentTime
            console.log(
              'Audio synced', current_audio.currentTime === video.currentTime
            )
          }

          if(!video.paused && current_audio.paused) {
            current_audio.play().catch(
              (function(audio) {
                return function(error) {
                  this.on_audio_play_error(error, audio)
                }
              })(current_audio).bind(this)
            )
          }
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
      var src_path = src.split("?")[0]
      if (/\.ass$/.test(src_path)) {
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
      } else if (/\.tra$/.test(src_path)) {
        var parts = src.split("/")
        if (parts.length > 4) {
          var stream_index = parts[3]
          this.request_transcoding(stream_index)
        }
      } else {
        var video = this.video()
        var track = document.createElement('track')

        track.setAttribute('src', src)
        track.setAttribute("kind", "subtitles")
        track.addEventListener("load", function(e) {
          var cues = e.target.track.cues
          for (var i = 0, il = cues.length; i < il; i++) {
            cues[i].line = 100 // bottom of screen, but not default -1
          }
        }, false)
        /*
        if (this.start_time) {
          var offset = this.start_time
          track.addEventListener("load", function(e) {
            // TODO: find a better way to clear activeCues list
            var cue_cache = []

            var cues = e.target.track.cues
            var currentTime = video.currentTime
            var new_start_time = new_end_time = null

            for (var i = 0, il = cues.length; i < il; i++) {
              new_start_time = cues[i].startTime - offset
              new_end_time = cues[i].endTime - offset

              cues[i].startTime = new_start_time
              cues[i].endTime = new_end_time

              if (
                new_start_time < currentTime
                || new_end_time < currentTime
              ) {
                e.target.track.removeCue(cues[i])
                cue_cache.push(cues[i])
                i = i - 1
                il = cues.length
              }
            }

            if (cue_cache.length) {
              setTimeout((function(textTrack, cue_cache) {
                return function() {
                  for (var i = 0, il = cue_cache.length; i < il; i ++)
                    textTrack.addCue(cue_cache[i])
                }
              })(e.target.track, cue_cache), 0)
            }
          }, false)
        }*/

        video.appendChild(track)
        video.textTracks[0].mode = "showing"
      }
    },
    set_audio: function(audio_id) {
      var current_audio = this.current_audio
      var video = this.video()
      var current_volume = 1
      if (current_audio !== null) {
        current_audio.pause()
        current_volume = current_audio.volume
      }

      var audio_el = this.wrapper.querySelector(
        'audio[data-audio-id="' + audio_id + '"]'
      )
      audio_el.volume = current_volume
      if (!video.paused) {
        audio_el.play().catch(
          (function(audio) {
            return function(error) {
              this.on_audio_play_error(error, audio)
            }
          })(audio_el).bind(this)
        )
      }
      this.current_audio = audio_el
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
        this.request_transcoding()
      }.bind(this), false)
      chrome_transcode.appendChild(chrome_transcode_btn)

      var chrome_transcode_cancel_btn = document.createElement("button")
      chrome_transcode_cancel_btn.innerHTML = "Cancel"
      chrome_transcode_cancel_btn.addEventListener("click", function() {
        this.wrapper.removeChild(chrome_transcode)
      }.bind(this), false)
      chrome_transcode.appendChild(chrome_transcode_cancel_btn)


      this.wrapper.appendChild(chrome_transcode)
    },
    close: function() {
      var video = this.wrapper.querySelector("video")
      video.pause()

      var duration = this.duration
      if (duration) {
        var watched = this.current_time() / duration
        if (watched > 0.9) {
          var els = document.querySelectorAll(
            '[data-id="' + this.media_id + '"] .js-played input'
          )
          for (var i = 0, il = els.length; i < il; i++) {
            els[i].checked = true
            window.onPlayedChange( { target: els[i] } )
          }
        } else if (watched > 0.05) {
          var resume_str = localStorage.getItem('resume')
          var resume = JSON.parse(resume_str) || {}
          resume[this.media_id] = Math.floor(this.current_time())
          localStorage.setItem('resume', JSON.stringify(resume))
        }
      }

      var audio = this.wrapper.querySelectorAll("audio")
      for (var i = 0, il = audio.length; i < il; i++) {
        audio[i].pause()
        var sources = audio[i].querySelectorAll("source")
        for (var j = 0, jl = sources.length; j < jl; j++){
          audio[i].removeChild(sources[j])
        }
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
      video.removeAttribute("src")
      video.load()

      document.body.removeChild(this.wrapper)
    },
    request_transcoding: function(subtitle_index) {
      this.set_state("buffering")
      if (this.current_audio !== null)
        this.current_audio.pause()

      if (subtitle_index === undefined)
        subtitle_index = null

      var video = this.video()
      var sources = video.querySelectorAll('source')
      var streams = []
      var source = source_src = null

      for (var i = 0, il = sources.length; i < il; i++) {
        source = sources[i]
        source_src = source.getAttribute("src")
        var params = get_params(source_src)

        if (
          params == null
          || (
            params.get("transcode") !== "vp9"
            || subtitle_index !== params.get("si")
          )
        ) {
          new_src = source_src.split("?")[0]
            + "?transcode=vp9&start="
            + Math.floor(this.current_time())
            + (subtitle_index !== null ? ("&si=" + subtitle_index) : "")
          streams.push(new_src)
        }
        video.removeChild(source)
      }

      if (streams.length) {
        this.create_sources(streams)
        video.load()
        console.log('transcoding video')
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
    restart_fullscreen_hide_ui_timeout: function(e) {
      this.fullscreen_show_ui()

      this.clear_fullscreen_hide_ui_timeout()

      this.fullscreen_hide_ui_timeout = setTimeout(
        this.fullscreen_hide_ui.bind(this),
        this.FULLSCREEN_HIDE_UI_TIMEOUT
      )
    },
    clear_fullscreen_hide_ui_timeout: function(e) {
      if (e) {
        e.stopPropagation()
      }

      if (this.fullscreen_hide_ui_timeout) {
        clearTimeout(this.fullscreen_hide_ui_timeout)
      }
    },
    on_fullscreen_changed: function(e) {
      var overlay = this.overlay()
      var controls = this.controls()

      if (document.fullscreen) {
        this.restart_fullscreen_hide_ui_timeout()

        controls.addEventListener(
          "mousemove",
          this.clear_fullscreen_hide_ui_timeout.bind(this),
          false
        )

        overlay.addEventListener(
          "mousemove",
          this.restart_fullscreen_hide_ui_timeout.bind(this),
          false
        )
      } else {
        if (controls) {
            controls.style.display = ""

            controls.removeEventListener(
              "mousemove",
              this.clear_fullscreen_hide_ui_timeout.bind(this),
              false
            )
        }

        if (overlay) {
          overlay.style.cursor = ""

          overlay.removeEventListener(
            "mousemove",
            this.restart_fullscreen_hide_ui_timeout.bind(this),
            false
          )
        }
      }
    },

    on_can_play: function(e) {
      var index = this._can_play.indexOf(e.target);
      if (index > -1) {
        this._can_play.splice(index, 1);
      }

      if (this._can_play.length == 0) {
        setTimeout(function() {
          this.video().play().then(
            function() {
              if (this.video().videoHeight === 0) {
                this.show_chrome_transcode()
              } else {
                this.set_state("playing")
              }
            }.bind(this)
          ).catch(this.on_video_play_error.bind(this))
        }.bind(this), this.BUFFER_TIME)
      }
    },
    on_audio_play_error: function(error, audio) {
      if (/The element has no supported sources./.test(error)){
        var current_src = audio.currentSrc
        var params = get_params(current_src)

        if (
          params == null
          || (params.get("transcode") !== "opus")
        ) {
          var start = params.get("start")
          new_src = current_src.split("?")[0]
            + "?transcode=opus"
            + (start ? ("&start=" + start) : "")
          audio.src = new_src
          audio.load()
          console.log("transcoding audio")
        }
      } else if (/NotAllowedError: play\(\) can only be initiated by a user gesture./.test(error)) {
        this.video().pause()
      } else {
        console.log('on_audio_play_error:', error)
      }
    },
    on_video_play_error: function(error){
      console.log('on_video_play_error:', error)
    }
  }

  return function (streams_obj) {
    console.log('Create player')
    new Player(streams_obj)
  }
})()
