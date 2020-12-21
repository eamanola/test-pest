# test-pest
Media Server, with anidb meta fetching integration

A little experiment with python

Features
- List video files in specified directories over http
- Attempt at minimal renaming
- Fetch art work/meta (limited to anidb)
- Play on server machine in selected media player (vlc) [playback can be started over http]
- Play locally in browser (tested on FF and chrome)
- Keeps track of shows being watched, next episodes, etc..

Road map
- UI / UX design
- new clients (android/ios/webos/etc..)
- 3rd party server ngix etc...
- big boy db maria, postgres, etc.. integration
- new meta sources imdb, tvdb, etc...

System requirements
- Python3
- FFMpeg

Developed on linux, with FF and chrome
- other platforms should work, but not tested

Install
- sudo apt get install ffmpeg python3
- git clone https://github.com/eamanola/test-pest.git
- cd test-pest && python3 server.py
- open browser http://localhost:8086

