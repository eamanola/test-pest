console.log('Web0S')

if (/Web0S/i.test(navigator.userAgent)) {
  Player.prototype.MERGE_ALL_AUDIO = true
  Player.prototype.FORCE_VTT = false
  Player.prototype.FORCE_VCODEC = "vp8"
}
