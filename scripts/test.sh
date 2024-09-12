#!/bin/bash

# Temporarily run+watch python script

if [ "$EUID" -ne 0 ]
  then echo "Please run this script as root"
  exit
fi

systemctl stop piano-led.service

# killall nodemon
killall python3

SCRIPT_DIR=$(dirname $(readlink -f $0))
pushd $SCRIPT_DIR/../src/python > /dev/null

while sleep 0.5; do
  ls -d *.py | entr -d -r python3 midi_pi.py
done