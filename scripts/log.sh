#!/bin/sh

# Tail logs from systemd service

journalctl -u piano-led.service -f -n 20