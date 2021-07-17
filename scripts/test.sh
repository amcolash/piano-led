#!/bin/bash

# Temporarily run python script

if [ "$EUID" -ne 0 ]
  then echo "Please run this script as root"
  exit
fi

SCRIPT_DIR=$(dirname $(readlink -f $0))
python3 $SCRIPT_DIR/../src/midi_pi.py