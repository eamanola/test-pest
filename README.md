# test-pest
Media Server, with anidb meta fetching integration

A little experiment with python

Features
- Scan for video files in specified directories
- Attempt at minimal renaming
- Fetch art work/meta (limited to anidb)
- List files, and control playback over http (in browser or mobile)
- Play on server machine in selected media player (vlc) [playback can be started from mobile, or other machine]
- Play locally in browser [limited, experimental] (tested on FF and chrome)
- Keeps track of shows being watched, next episode, seen episodes/shows and suggests the day's anime menu

Road map
- test on win / mac
- resume playback in next
- UI / UX design
- reach beta
- new api clients (android/ios/webos/etc..)
- 3rd party server ngix etc...
- big boy db maria, postgres, etc.. integration
- new meta sources imdb, tvdb, etc...

Need
- co devs
- alpha testers

System requirements
- Python3
- FFMpeg

Developed on linux, with FF and chrome
- other platforms should work, but not tested

Setup: run python3 server.py in root dir, and open printed address in browser. Expect crash poks

