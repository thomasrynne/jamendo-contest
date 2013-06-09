function action(prefix, value) {
    /* here we emulate the mpd behaviour in a browser */
    if (prefix == "jamendo-track") {
        playTrack(value)
    } else if (prefix == "jamendo-album") {
        playAlbum(value)
    } else if (prefix == "jamendo-radio") {
        playRadio(value)
    } else if (prefix == "action") {
        if (value == "mpd.stop") { stop() }
        else if (value == "mpd.pause") { pause() }
        else if (value == "mpd.next") { next() }
        else if (value == "mpd.previous") { previous() }
        else { status("Unknown action: " + value) }
    } else {
        status("Unknown: " + prefix)
    }
}
function cancelRecord() {
    card_mode = play_mode
    reader("Ready")
}
function playAlbum(albumid) {
    $.ajax({
      url: "http://api.jamendo.com/v3.0/albums/tracks",
      data: { 'client_id': "6154a905", "id": albumid },
      dataType: "json",
      timeout: 5000,
      error: function() {
        $("#messages").append("Track lookup for " + trackid + " failed")
      },
      success: function(data) {
        tracks = data["results"][0]["tracks"]
        play(
          $.map(tracks, function(track) { return { url: trackStream(track["id"]), name: track["name"] } })
        )
      }
    })
}
function trackStream(trackid) { return "http://api.jamendo.com/v3.0/tracks/file?client_id=6154a905&id=" + trackid }
function playTrack(trackid) {
    $.ajax({
      url: "http://api.jamendo.com/v3.0/tracks",
      data: { 'client_id': "6154a905", "id": trackid },
      dataType: "json",
      timeout: 5000,
      error: function() {
        $("#messages").append("Track lookup for " + trackid + " failed")
      },
      success: function(data) {
        play([ {url: trackStream(trackid), name: name} ])
      }
    })
}
function playRadio(code) {
    $.ajax({
      url: "http://api.jamendo.com/v3.0/radios/stream",
      data: { 'client_id': "6154a905", "name": code},
      dataType: "json",
      timeout: 5000,
      error: function() {
        $("#messages").append("Track lookup for " + trackid + " failed")
      },
      success: function(data) {
        var result = data["results"][0]
        play([ {url:result["stream"], name: result["dispname"]} ])
      }
    })
}
function next() {
    if ((playlist_cursor+1) < playlist.length) { playlist_cursor++; doplay() }
}
function previous() {
    if (playlist_cursor > 0) { playlist_cursor++; doplay() }
}
playlist = []
playlist_cursor = 0
sound = undefined
function play(newplaylist) {
    playlist = newplaylist
    playlist_cursor = 0
    doplay()
}
function doplay() {
    soundManager.stopAll()
    if (sound) {
        sound.destruct()
    }
    sound = soundManager.createSound({
      url: playlist[playlist_cursor].url,
      onfinish: function(){
          playlist_cursor ++
          if (playlist_cursor >= playlist.length) {
            playlist_cursor = 0
            player("Stopped")
          } else { //play next track in album
            doplay()
          }
      }
    })
    sound.play()
    player(playlist[playlist_cursor].name)
}
function stop() {
    if (sound) { sound.stop(); player("Stopped") } 
}
function pause() {
    if (sound) {
        sound.togglePause()
        if (sound.paused) { player("Paused") } else { player(playlist[playlist_cursor].name) }
    } 
}

function lookupCard(card, callback) {
    if (use_local_storage) {
        var local = window.localStorage.getItem("CARD:" + card)
        if (local) { callback(local); return }
    }
    $.ajax({
      url: "/cardservice/read",
      data: { 'cardnumber': card},
      dataType: "json",
      timeout: 15000,
      error: function() {
        status("Unknown card")
      }, 
      success: function(data) {
        var entry = data[0]
        var uri = entry["type"] + ":" + entry["value"]
        callback(uri)
        if (use_local_storage) { window.localStorage.setItem("CARD:"+card, uri) }
      }
    })
    
}
var play_mode = function(card) {
    uri = lookupCard(card, function(uri) {
        var parts = uri.split(":")
        var actionType = parts[0]
        var actionValue = parts[1]
        action(actionType, actionValue)
    })
}
function reader(text) {
     $('#reader').html(text)
}
function player(text) {
     $('#mpd').html(text)
}
function status(text) {
     $('#status').html(text)
}

function record(actionType, actionValue, name) {
    reader("Record mode for " + name)
    card_mode = function(card) {
       $('#reader').html("Storing...")
       if (use_local_storage) { window.localStorage.setItem("CARD:"+card, actionType + ":" + actionValue) }
       var jsonText = JSON.stringify({ "type": actionType, "value": actionValue, "name": name})
       $.ajax({
         type: "POST",
         url: "/cardservice/store",
         datatype: "text",
         data: { 'cardnumber': card, "value":  jsonText },
         timeout: 10000,
         error: function() {
           status("Remote saving failed")
         }, 
         success: function(data) { reader("Ready") }
       })
       card_mode = play_mode
    }
}
var card_mode = play_mode
var use_local_storage = false
try {
  localStorage.setItem("test_support", "123")
  localStorage.removeItem("test_support")
  use_local_storage = true
} catch(e) {}
function listenToKeys() {
    var key_buffer = []
    var last_number_press = 0
    document.onkeypress=function(event) {
        var unicode=event.keyCode? event.keyCode : event.charCode
        var key = unicode-48
        if (key >= 0 && key <= 9) {
            if (key != 0 || key_buffer.length > 0) { /*ignore the leading 000 as this is not reliable */
                var now = new Date().getTime()
                if ( (now - last_number_press) > 5000) {
                    key_buffer = []
                }
                last_number_press = now
                key_buffer.push(key)
                if (key_buffer.length == 7) {
                    var card_number = key_buffer.join("")
                    setTimeout(function() { card_mode(card_number) }, 1)
                    key_buffer = []
                }
            }
        }
    }
    if (document.hasFocus) { reader("Ready") } else { reader("Click window to get focus") }
    window.onfocus = function() { reader("Ready") }
    window.onblur = function() { reader("Click on window to get focus") }
}
function initPlayer() {
    soundManager.setup({
        url: '/assets/',
        debugMode: false,
        onready: function() { player("Stopped") },
        ontimeout: function() { player("Player not avaliable") }
    });
}

$(document).ready(initPlayer)
$(document).ready(listenToKeys)


