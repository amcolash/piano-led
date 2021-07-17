#!/bin/bash

# Restart systemd service, must be run as root

if [ "$EUID" -ne 0 ]
  then echo "Please run this script as root"
  exit
fi

systemctl restart piano-led.service