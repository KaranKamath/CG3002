#!/bin/bash
# Source: alexba.in/blog/2015/01/14/automatically-reconnecting-wifi-on-a-raspberrypi/

function log {
    echo "echo $(date '+%Y-%m-%d %H:%M:%S') $1" >> /home/pi/logs/wifi_reconnect.log
}

# 8.8.8.8 is a public Google DNS server
SERVER=8.8.8.8

# Only send two pings, sending output to /dev/null
ping -c2 ${SERVER} > /dev/null

# If the return code from ping ($?) is not 0 (meaning there was an error)
if [ $? != 0 ]
then
    # Restart the wireless interface
    "Network down...restarting"
    sudo ifdown --force wlan0
    sudo ifup wlan0
else
    log "Network up"
fi