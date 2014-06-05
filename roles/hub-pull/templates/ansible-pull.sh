#!/bin/bash

. /etc/profile
. $HOME/.profile
cd "{{ home }}"

if ansible-pull -C "{{ deploy_rev }}" \
                -i "{{ home }}/inventory.ini" \
                -d "{{ deploy }}" \
                -U "{{ deploy_repo }}" \
                >> {{ logfile }} 2>&1;
then
    rm "{{ logfile }}"
else
    SYNCED_LOGFILE="{{ synced_logfile }}"
    sudo mv "{{ logfile }}" "$SYNCED_LOGFILE"
    sudo chown smarthome:smarthome "$SYNCED_LOGFILE"
fi
