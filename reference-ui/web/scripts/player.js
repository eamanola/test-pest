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

  if (this.MERGE_ALL_AUDIO) {
    this.MERGE_FIRST_AUDIO = true
  }

  wrapper.appendChild(this.create_video())

  if (this.USE_ASS_JS) {
    wrapper.appendChild(this.create_subtitle_container())
  }
  wrapper.appendChild(this.create_loading())
  wrapper.appendChild(this.create_overlay())
  wrapper.appendChild(this.create_volume_display())

  var controls = this.create_controls()
  controls.appendChild(this.create_close_btn())
  controls.appendChild(this.create_fullscreen_btn())
  wrapper.appendChild(controls)

  document.addEventListener(
    "fullscreenchange",
    this.on_fullscreen_changed.bind(this),
    false
  );

  try {
    document.body.prepend(wrapper)
  } catch(e) {
    document.body.appendChild(wrapper)
  }

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
  hide_volume_timeout: null,
  HIDE_VOLUME_TIMEOUT: 5 * 1000,
  ENABLE_SEEK: true,
  MERGE_ALL_AUDIO: false,
  MERGE_FIRST_AUDIO: false,
  ENABLE_CHAPTERS: true,
  V_AUDIO: null,
  FORCE_VTT: false,
  FORCE_VCODEC: null,
  USE_ASS_JS: false,
  fonts: null,
  chapters: null,
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

    var resume_str = localStorage.getItem('resume')
    var resume = JSON.parse(resume_str) || {}
    if (resume[this.media_id] && typeof(resume[this.media_id]) === "number")
      this.start_time = resume[this.media_id]

    this.create_sources(streams_obj)

    var min_audio = this.MERGE_FIRST_AUDIO ? 1 : 0
    if (streams_obj.audio.length > min_audio) {
      if (streams_obj.audio.length > 1) {
        this.controls()
          .appendChild(this.create_audio_select(streams_obj.audio))
      }

      if (!this.MERGE_ALL_AUDIO) {
        this.create_audio(streams_obj.audio)
        this.sync_audio()
      }
    }
    if (!this.MERGE_ALL_AUDIO) {
      var selected_audio;
      if (streams_obj.audio.length > 1) {
        selected_audio = this.audio_select().value
      } else if (streams_obj.audio.length == 1) {
        selected_audio = streams_obj.audio[0].id
      }
      if (selected_audio !== undefined){
        this.set_audio(selected_audio)
      }
    }

    // create after sources, in case default subtitle requires re-transcoding
    if (streams_obj.subtitles.length > 0) {
      if (this.USE_ASS_JS) {
        if (streams_obj.fonts.length > 0) {
          this.fonts = []
          this.load_fonts(streams_obj.fonts)
        }
      } else {
        this.fonts = streams_obj.fonts
      }
      this.controls()
        .appendChild(this.create_subtitle_select(streams_obj.subtitles))
    }

    if (this.ENABLE_CHAPTERS) {
      if (streams_obj.chapters.length) {
        this.chapters = streams_obj.chapters
        this.controls().appendChild(this.create_prev_chapter_button())
        this.controls().appendChild(this.create_next_chapter_button())
      }
    }

    this.controls().appendChild(this.create_play_position())

    this.video().load()
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
  volume_display: function() {
    return this.wrapper.querySelector(".volume-display")
  },
  audio_select: function() {
    return this.wrapper.querySelector(".audio-select")
  },
  subtitle_select: function() {
    return this.wrapper.querySelector(".subtitle-select")
  },
  subtitle_container: function() {
    return this.wrapper.querySelector(".subtitle-container")
  },
  prev_chapter_button: function() {
    return this.wrapper.querySelector(".previous-chapter")
  },
  next_chapter_button: function() {
    return this.wrapper.querySelector(".next-chapter")
  },

  create_video: function() {
    var video = document.createElement('video')
    //v.setAttribute("width", "640")
    // v.setAttribute("controls", "1")
    // v.muted = true
    video.autoplay = false
    video.preload = "none"
    video.muted = !this.MERGE_FIRST_AUDIO

    video.addEventListener("error", console.error, false)

    // ? check effect tonight
    video.addEventListener("ended", function() {
      //this.close.bind(this)
      history.go(-1)
    }, false)

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
              (player.start_time + buffered_end) / duration * 100 + '%'
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
        sessionStorage.setItem('volume', new_volume)
        this.show_volume_display()
      }
    }.bind(this), false)

    return overlay
  },
  create_volume_display: function() {
    var span = document.createElement('span')
    span.className = "volume-display black-text-stroke"
    return span
  },
  create_controls: function() {
    var controls = document.createElement('div')
    controls.className = "video-controls"

    return controls
  },
  create_close_btn: function() {
    var close_button = document.createElement('button')
    close_button.addEventListener("click", function() {
      // this.close.bind(this)
      history.go(-1)
    }, false)
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
      var duration = this.duration

      if (duration) {
        var percent = (e.layerX / play_position_total.offsetWidth)
        if (percent < 0.025) percent = 0

        var new_time = percent * duration
        this.seek(new_time)
      }
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
    audio_select.className = "audio-select"

    audio_select.addEventListener("change", function() {
      this.set_audio(audio_select.value)
    }.bind(this), false)

    for (var i = 0, il = audio_obj.length; i < il; i++) {
      audio_option = document.createElement('option')
      audio_option.setAttribute("value", audio_obj[i].id)
      var title = audio_obj[i].title
      var lang = audio_obj[i].lang
      if (title) {
        // title += lang ? (" (" + lang + ")") : ""
      } else if (lang) {
        title = lang
      } else {
        title = "Unknown"
      }

      audio_option.innerHTML = title
        + (audio_obj[i].forced ? " (forced)" : "")
        + (audio_obj[i].default ? " (default)" : "")

      audio_select.appendChild(audio_option);

      if (audio_obj[i].default == true) {
        audio_option.setAttribute("selected", "selected")
      }
    }

    return audio_select
  },
  create_subtitle_select: function(subtitles) {
    var subtitle_select = document.createElement("select")
    subtitle_select.className = "subtitle-select"

    subtitle_select.addEventListener("change", function() {
      this.set_subtitle(subtitle_select.value)
    }.bind(this), false)

    var subtitle_option = document.createElement("option")
    subtitle_option.value = ""
    subtitle_option.innerHTML = "Off"
    subtitle_select.appendChild(subtitle_option)

    var subtitle = null, title, lang, label = null, subtitle_option = null
    for (var i = 0, il = subtitles.length; i < il; i ++) {
      subtitle = subtitles[i]
      title = subtitle.title
      lang = subtitle.lang
      if (title) {
        // title += lang ? (" (" + lang + ")") : ""
      } else if (lang) {
        title = lang
      } else {
        title = "Unknown"
      }
      label = title
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
  create_subtitle_container: function() {
    var div = document.createElement("div")
    div.className = "subtitle-container"

    return div
  },
  create_prev_chapter_button: function() {
    var button = document.createElement("button")
    button.className = "previous-chapter"
    button.innerHTML = "<"
    button.addEventListener("click", this.prev_chapter.bind(this), false)

    return button
  },
  create_next_chapter_button: function(){
    var button = document.createElement("button")
    button.className = "next-chapter"
    button.innerHTML = ">"
    button.addEventListener("click", this.next_chapter.bind(this), false)

    return button
  },

  create_sources: function(stream_obj) {
    var video = this.video()
    var error_count = 0
    var source = document.createElement('source')

    source.addEventListener("error", function(e) {
      error_count = error_count + 1
      var source_length = video.querySelectorAll('source').length
      console.log(error_count + '/' + source_length, e)
      if (error_count == source_length) {
        this.request_transcoding()
      }
    }.bind(this), false)

    video.appendChild(source)

    var cv = null
    if (!MediaSource.isTypeSupported(stream_obj.video[0].type)) {
      if (this.FORCE_VCODEC) {
        cv = this.FORCE_VCODEC
      } else if (MediaSource.isTypeSupported('video/webm; codecs="vp9"')) {
        cv = "vp9"
      } else {
        cv = "vp8"
      }
    }

    var a = null, ca = null;
    if (this.MERGE_FIRST_AUDIO) {
      if (stream_obj.audio.length > 0) {
        var audio_track = stream_obj.audio[0]
        a = audio_track.id
        this.V_AUDIO = a

        var audioEl = document.createElement("audio")
        if (!audioEl.canPlayType(audio_track.type)) {
          if (audioEl.canPlayType('audio/ogg; codecs=opus')){
            ca = "opus"
          } else {
            ca = "vorbis"
          }
        }
      }
    }

    var pvideo = { v: "0", cv: cv }
    var paudio = null
    if (a || ca)
      paudio = { a: a, ca: ca }
    var psubtitle = null
    var pstart = null

    this.set_video(pvideo, paudio, psubtitle, pstart)
  },
  create_audio: function(audio_obj) {
    var audio = null, source = null

    var audioEl = document.createElement("audio"), acodec = null
    if (audioEl.canPlayType('audio/ogg; codecs=opus'))
      acodec = "opus"
    else
      acodec = "vorbis"

    var discard_audio = this.MERGE_FIRST_AUDIO ? 1 : 0

    for (var i = discard_audio, il = audio_obj.length; i < il; i++) {
      audio = document.createElement('audio')
      // audio.setAttribute("type", "audio/ogg")
      audio.setAttribute("data-audio-id", audio_obj[i].id)
      // audio.setAttribute("controls", "1")
      audio.preload = "auto"
      audio.autoplay = false
      audio.style.display = "none"

      source = document.createElement("source")

      var src = [
        "/av/", this.media_id,
        "?a=", audio_obj[i].id,
        "&start=", this.start_time
      ]
      if (!audioEl.canPlayType(audio_obj[i].type)) {
        src.push("&ca=", acodec)
      }
      source.setAttribute("src", src.join(""))

      source.addEventListener("error", console.error, false)
      audio.appendChild(source)

      this.wrapper.appendChild(audio);
    }
  },
  load_fonts: function(fonts_obj) {
    for (var i = 0, il = fonts_obj.length; i < il; i++) {
      // var ff = new FontFace("CronosPro-Bold", "url(/fonts/10845a2f096febc4103e79f9ceff6b1d/CronosPro-Bold.ttf)")
      console.log(fonts_obj[i])
      var family = fonts_obj[i].family
      var url = fonts_obj[i].url

      var famalies = family.split(", ")
      for (var j = 0, jl = famalies.length; j < jl; j++) {
        var ff = new FontFace(famalies[j], "url(" + encodeURI(url) + ")");
        (function(ff){
          ff.load().then(function(res) {
              document.fonts.add(ff)
              this.fonts.push(ff)
              console.log('yep', ff)
            }.bind(this)).catch(function(res) {
              console.log("Fail", res, ff)
            }.bind(this))
        }.bind(this))(ff)
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
    if (src && this.FORCE_VTT) {
      src = src.slice(0, -3) + "vtt"
    }

    var video = this.video()
    var old_tracks = video.querySelectorAll("track")
    for (var i = 0, il = old_tracks.length; i < il; i ++) {
      video.removeChild(old_tracks[i])
    }

    if (this.ass_renderer !== null) {
      try {
        if (this.USE_ASS_JS) {
          this.ass_renderer.hide()
        } else {
          this.ass_renderer.freeTrack()
        }
      } catch (e) {
        console.log('ass render', e)
      }
    }

    var hardcoded_sub = /si=\d+$/.test(video.currentSrc)
    if (hardcoded_sub) {
      var new_sub_needs_hard_code = /\.tra$/.test(src)
      if (!new_sub_needs_hard_code) {
          // remove old hard code
          this.request_transcoding()
      }
    }

    if (src) {
      var src_path = src.split("?")[0]
      if (/\.ass$/.test(src_path)) {
        try {
          if (this.USE_ASS_JS) {
            ajax(src + "?start=" + this.start_time, function(responseText) {
              this.ass_renderer = new ASS(responseText, this.video(), {
                // Subtitles will display in the container.
                // The container will be created automatically if it's not provided.
                container: this.subtitle_container(),  //document.getElementById('my-container'),

                // see resampling API below
                resampling: 'video_width',
              });
              window.addEventListener("resize", function() {
                if (this.ass_renderer) {
                  this.ass_renderer.resize()
                }
              }.bind(this), false)
            }.bind(this))
          } else if (this.ass_renderer === null) {
            this.ass_renderer = new SubtitlesOctopus({
              video: this.video(),
              subUrl: src + "?start=" + this.start_time,
              fonts: this.fonts,
              workerUrl: '/scripts/octopus-ass/subtitles-octopus-worker.js',
              legacyWorkerUrl: '/scripts/octopus-ass/subtitles-octopus-worker-legacy.js'
            })
          } else {
            this.ass_renderer.setTrackByUrl(src + "?start=" + this.start_time)
          }
        } catch (e) {
          console.log('ass render', e)
        }
      } else if (/\.tra$/.test(src_path)) {
        var parts = src.split("/")
        if (parts.length > 4) {
          var stream_index = parts[3]
          this.set_video(null, null, { s: stream_index }, null)
        }
      } else {
        var video = this.video()
        var track = document.createElement('track')

        track.setAttribute('src', src + "?start=" + this.start_time)
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
    }
  },
  set_audio: function(audio_id) {
    if (this.MERGE_ALL_AUDIO) {
      return this.merge_audio(audio_id)
    }

    var current_audio = this.current_audio
    var video = this.video()
    var current_volume = 1
    if (current_audio !== null) {
      current_volume = current_audio.volume
    } else {
      var volume = sessionStorage.getItem('volume')
      current_volume = volume ? +volume : current_volume
    }

    if (current_audio !== null) {
      if (current_audio != video) {
        current_audio.pause()
      } else {
        video.muted = true
      }
    }

    if (audio_id != this.V_AUDIO) {
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
    } else {
      video.volume = current_volume
      this.current_audio = video
      video.muted = false
    }
  },
  set_video: function(pvideo, paudio, psubtitle, pstart) {
    console.log('set_video')
    var video = this.video()

    var source = video.querySelector("source")
    var params = get_params(source.src)
    var v, cv, a, ca, s;
    var v = pvideo && pvideo.v ? pvideo.v : params.get("v")
    var cv = pvideo && pvideo.cv ? pvideo.cv : params.get("cv")
    var a = paudio && paudio.a ? paudio.a : params.get("a")
    var ca = paudio && paudio.ca ? paudio.ca : params.get("ca")
    var s = psubtitle && psubtitle.s ? psubtitle.s : params.get("s")

    if (
      v == params.get("v")
      && cv == params.get("cv")
      && a == params.get("a")
      && ca == params.get("ca")
      && s == params.get("s")
      && pstart == null
    ) {
      console.log('skip')
      return
    }

    video.pause()
    this.set_state("buffering")

    var current_time = pstart != null ? pstart : this.current_time()
    var start = current_time > 10 ? current_time : 0

    this.start_time = start

    var new_src = "/av/" + this.media_id
      + "?v=0"
      + (cv != null ? ("&cv=" + cv) : "")
      + (a != null ? ("&a=" + a) : "")
      + (ca != null ? ("&ca=" + ca) : "")
      + (s != null ? ("&s=" + s) : "")
      + "&w=" + screen.width
      + "&h=" + screen.height
      + (start ? ("&start=" + start) : "")

    console.log(new_src)
    source.setAttribute("src", new_src)
    video.load()
  },
  merge_audio: function(audio_id) {
    this.set_video(null, { a: audio_id }, null, null)
    // update start_time
    this.set_subtitle(this.subtitle_select().value)
  },
  in_buffered: function(secs) {
    console.log(secs, this.start_time)
    if (secs >= this.start_time) {
      var video = this.video()
      var buffered = video.buffered
      var time = secs - this.start_time
      console.log(time)
      for (var i = 0, il = buffered.length; i < il; i ++) {
        console.log(buffered.start(i), buffered.end(i))
        if (buffered.start(i) <= time && buffered.end(i) > time) {
          return true
        }
      }
    }

    return false
  },
  seek: function(secs) {
    var duration = this.duration
    if (duration){
      this.play_position_played().style.width =
        this.play_position_buffered().style.width =
          (secs / duration * 100) + "%"
    }
    this.play_position_time().innerHTML = format_secs(secs)

    if (this.in_buffered(secs)) {
      console.log('in buffered')
      this.video().currentTime = secs - this.start_time
      return
    }

    console.log('server seek')

    var video = this.video()
    if (!video.paused) {
      video.pause()
      function play() {
        video.removeEventListener("canplay", play, false)
        video.play().catch(this.on_video_play_error.bind(this))
        console.log('play')
      }
      video.addEventListener("canplay", play.bind(this), false)
    }


    this.set_video(null, null, null, secs)

    if (!this.MERGE_ALL_AUDIO) {
      var audio = this.wrapper.querySelectorAll("audio")
      for (var i = 0, il = audio.length; i < il; i++) {
        var sources = audio[i].querySelectorAll("source")
        for (var j = 0, jl = sources.length; j < jl; j++) {
          var current_src = sources[j].src
          current_src = current_src
            .replace(/start=\d+[&]?/, "").replace(/&?$/, "")

          sources[j].src = current_src + "&start=" + this.start_time
        }
        audio[i].load()
      }
    }

    this.set_subtitle(this.subtitle_select().value)
  },
  next_chapter: function() {
    var current_chapter = this.current_chapter()
    var next_chapter = current_chapter + 1
    if (next_chapter < this.chapters.length) {
      this.set_chapter(next_chapter)
    }
  },
  prev_chapter: function() {
    var current_chapter = this.current_chapter()
    var chapter_start_time = this.chapters[current_chapter].start_time
    var offset = -1
    if (this.current_time() > chapter_start_time + 10) {
      offset = 0
    }

    var prev_chapter = current_chapter + offset
    if (prev_chapter >= 0) {
      this.set_chapter(prev_chapter)
    }
  },
  current_chapter: function() {
    var current_time = this.current_time()
    for (var i = 0, il = this.chapters.length; i < il; i++) {
      var chapter = this.chapters[i]
      if (chapter.start_time <= current_time
        && chapter.end_time > current_time)
        return i
    }
  },
  set_chapter: function(index) {
    if (index < 0 || index > this.chapters.length - 1) {
      return
    }

    var chapter = this.chapters[index]
    this.seek(chapter.start_time)
    console.log(chapter, chapter.title)
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
  show_volume_display: function() {
    var current_audio = this.current_audio
    if (current_audio) {
      var volume_display = this.volume_display()
      volume_display.innerHTML = Math.round(current_audio.volume * 100) + '%'
      volume_display.style.display = "initial"

      if (this.hide_volume_timeout) {
        clearTimeout(this.hide_volume_timeout)
      }

      this.hide_volume_timeout = setTimeout(function() {
        var volume_display = this.volume_display()
        volume_display.style.display = ""
      }.bind(this), this.HIDE_VOLUME_TIMEOUT)
    }
  },
  close: function() {
    var video = this.wrapper.querySelector("video")
    video.pause()

    var duration = this.duration
    if (duration) {
      var watched = this.current_time() / duration
      if (watched > 0.9) {
        set_played(this.media_id)
      } else if (watched > 0.05) {
        var resume_str = localStorage.getItem('resume')
        var resume = JSON.parse(resume_str) || {}
        resume[this.media_id] = +this.current_time().toFixed(3)
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
        if (this.USE_ASS_JS) {
          this.ass_renderer.destroy()
          if (this.fonts) {
            for (var i = 0, il = this.fonts.length; i < il; i ++) {
              document.fonts.delete(this.fonts[i])
            }
          }
        } else {
          this.ass_renderer.dispose()
        }
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
    console.log('transcoding video')

    this.set_state("buffering")
    if (this.current_audio !== null)
      this.current_audio.pause()

    if (subtitle_index === undefined)
      subtitle_index = null

    var pvideo = { v: null, cv: this.FORCE_VCODEC ? this.FORCE_VCODEC : "vp9" }
    var paudio = { a: null, ca: "opus" }
    var psubtitle = subtitle_index ? { s: subtitle_index } : null
    var pstart = null

    this.set_video(pvideo, paudio, psubtitle, pstart)
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
              if (this.USE_ASS_JS) {
                if (this.ass_renderer) {
                  this.ass_renderer.resize()
                }
              }
            }
          }.bind(this)
        ).catch(this.on_video_play_error.bind(this))
      }.bind(this), this.BUFFER_TIME)
    }
  },
  on_audio_play_error: function(error, audio) {
    if (/The element has no supported sources./.test(error)){
      console.log("transcoding audio")
      var current_src = audio.currentSrc
      var params = get_params(current_src)

      if (params.get("ca") !== "opus") {
        audio.src = [
          "/av/", this.media_id,
          "?a=", params.get("a"),
          "&start=", this.start_time,
          "&ca=opus"
        ].join("")

        audio.load()
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

function create_player(streams_obj) {
  console.log('Create player')
  window._player = new Player(streams_obj)
  history_push_state("player", null)
}
