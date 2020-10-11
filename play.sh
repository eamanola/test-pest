#!/bin/sh

mpv --slang=en,eng --title="testpest" "$@" &
sleep 0.8
wmctrl -r testpest -e 0,1920,46,1920,1056
fg
