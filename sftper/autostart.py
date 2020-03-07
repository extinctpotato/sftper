import subprocess, os
from pathlib import Path

SERVICE='''
[Unit]
Description=sftper - mounting helper

[Service]
ExecStart=/usr/bin/sftper
Type=simple

[Install]
WantedBy=default.target
'''

HOME = str(Path.home())
UNIT_PATH = os.path.join(HOME, ".config/systemd/user/sftper.service")

def start():
    with open(UNIT_PATH, 'w') as f:
        f.write(SERVICE)

    subprocess.check_call("systemctl --user daemon-reload", shell=True)
    subprocess.check_call("systemctl --user enable sftper", shell=True)
    subprocess.check_call("systemctl --user start sftper", shell=True)

def stop():
    subprocess.check_call("systemctl --user stop sftper", shell=True)
    subprocess.check_call("systemctl --user disable sftper", shell=True)
    subprocess.check_call("systemctl --user daemon-reload", shell=True)
    os.remove(UNIT_PATH)

