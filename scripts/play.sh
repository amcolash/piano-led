#!/bin/bash

SCRIPT_DIR=$(dirname $(readlink -f $0))
PORT="System MIDI In"

function playDir() {
  for f in `find "$1" -name '*.mid' -print | shuf`
  do
    echo $f
    aplaymidi --port="$PORT" $f
  done
}

if [ "$#" -eq 1 ]; then
  if [ -f "$1" ]; then
    aplaymidi --port="$PORT" $1
  else
    playDir $1
  fi
else
  playDir $SCRIPT_DIR/../midi
fi
