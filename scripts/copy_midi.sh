#!/bin/sh

SCRIPT_DIR=$(dirname $(readlink -f $0))

rsync -avh $SCRIPT_DIR/../midi/ pi1:~/piano-led/midi/ --delete