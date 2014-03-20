#!/usr/bin/env python

import sys
import os.path
import re

HOME = sys.argv[1]
CONFIG_DIR = sys.argv[2]

PATH = "/etc/wpa_supplicant/wpa_supplicant.conf"
TOKEN = "###SMARTHOME-MAGIC-TOKEN###"

with open(PATH) as f:
    sys_cfg = f.read()
    sys_cfg = sys_cfg.split(TOKEN)[0].strip()
    sys_cfg += '\n\n' + TOKEN + '\n\n'

with open(os.path.join(CONFIG_DIR, "wlan.cfg")) as f:
    cfg = f.read()

with open(os.path.expanduser('~smarthome/.hub-id')) as f:
    UUID = f.read().strip()
with open(os.path.expanduser('~smarthome/.hub-classes')) as f:
    classes = re.split(r'[^a-z0-9-]+', f.read().strip())

for name in classes + [UUID]:
    cfg_path = os.path.join(CONFIG_DIR, "hubs", name, "wlan.%s.cfg" % name)
    if os.path.isfile(cfg_path):
        cfg = open(cfg_path).read()

with open(PATH, 'w') as f:
    f.write(sys_cfg + cfg)
