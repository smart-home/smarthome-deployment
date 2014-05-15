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

config_paths = {}
for root, dirs, files in os.walk(CONFIG_DIR):
    foldername = os.path.basename(root)
    if not "wlan.%s.cfg" % foldername in files:
        continue
    if foldername in config_paths:
        config_paths[foldername] = None
        # TODO: log an error here
    else:
        config_paths[foldername] = os.path.join(root, "wlan.%s.cfg" % foldername)

for name in classes + [UUID]:
    if not config_paths.get(name): continue
    cfg_path = config_paths[name]
    cfg = open(cfg_path).read()

with open(PATH, 'w') as f:
    f.write(sys_cfg + cfg)
