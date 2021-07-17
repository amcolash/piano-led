#!/bin/bash

# Install systemd service, must be run as root

if [ "$EUID" -ne 0 ]
  then echo "Please run this script as root"
  exit
fi

echo Copying Service
cp piano-led.service /etc/systemd/system/piano-led.service

echo Reloading Daemon
systemctl daemon-reload

echo Enabling Service
systemctl enable piano-led.service

echo Starting Service
systemctl start piano-led.service

echo Service Installed