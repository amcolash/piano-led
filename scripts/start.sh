#!/bin/bash

# Start systemd service, must be run as root

if [ "$EUID" -ne 0 ]
  then echo "Please run this script as root"
  exit
fi

systemctl start piano-led.service