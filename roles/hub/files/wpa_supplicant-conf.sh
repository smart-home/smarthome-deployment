#!/bin/bash

HOME=$1
CONFIGDIR=$2

cat "$CONFIGDIR/wlan.cfg" > /etc/wpa_supplicant/wpa_supplicant.conf

UUID=$(cat $HOME/.hub-id)
HUB_CONFIG="$CONFIGDIR/$UUID/wlan.$UUID.cfg"
if [ -f "$HUB_CONFIG" ]
then
    cat "$HUB_CONFIG" >> /etc/wpa_supplicant/wpa_supplicant.conf
fi
