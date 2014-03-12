import subprocess
import os
import sys
import re

original_command = os.getenv('SSH_ORIGINAL_COMMAND')
if not original_command: sys.exit(42)

# print original_command

last_arg = original_command.split(' ')[-1]
if not re.match(r'^[a-zA-Z0-9/-]+$', last_arg): sys.exit(42)

path = 'smarthome/' + last_arg
# print path

rsync_cmd = ["rsync", "--server", "-vlogDtprz", "--timeout=30", "--append", ".", path]
subprocess.call(rsync_cmd)
