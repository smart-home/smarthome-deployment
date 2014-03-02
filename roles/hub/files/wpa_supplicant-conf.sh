#!/bin/bash

HOME=$1
CONFIGDIR=$2

OLD=/etc/wpa_supplicant/wpa_supplicant.conf
NEW=/etc/wpa_supplicant/wpa_supplicant.conf.new

awk '/###SMARTHOME-MAGIC-TOKEN###/ {exit} {print}' $OLD > $NEW

echo '###SMARTHOME-MAGIC-TOKEN###' >> $NEW

UUID=$(cat $HOME/.hub-id)
HUB_CONFIG="$CONFIGDIR/$UUID/wlan.$UUID.cfg"
if [ -f "$HUB_CONFIG" ]
then
    cat "$HUB_CONFIG" >> $NEW
else
    cat "$CONFIGDIR/wlan.cfg" >> $NEW
fi

mv $NEW $OLD
