#!/usr/bin/env python3

import sys, signal, os
from fstab import Fstab
from time import sleep
from PyQt5 import QtWidgets, QtGui, QtCore
from pathlib import Path
import subprocess

def home_to_tilde(path):
    return path.replace(str(Path.home()), "~")

class RightClickMenu(QtWidgets.QMenu):
    def __init__(self, parent=None):
        QtWidgets.QMenu.__init__(self, "Test", parent=None)
        self.parent = parent

        self.aboutToShow.connect(self.check_if_mount)

        f = Fstab()
        f.read()

        for line in f.lines:
            if line.dict['fstype'] == 'fuse.sshfs':
                mdir = line.dict['directory']

                fstab_entry = QtWidgets.QMenu("{}".format(home_to_tilde(mdir)), self)

                mount_action = QtWidgets.QAction("Mount", self)
                mount_action.triggered.connect(lambda checked, a=mdir: self.mount(checked,a))

                open_action = QtWidgets.QAction("Open in file manager", self)
                open_action.triggered.connect(lambda checked, a=mdir: self.xdg_open(checked,a))

                fstab_entry.addAction(mount_action)
                fstab_entry.addAction(open_action)

                self.addMenu(fstab_entry)

    def check_if_mount(self):
        mount = QtGui.QIcon.fromTheme("network-transmit-receive-symbolic")
        umount = QtGui.QIcon.fromTheme("network-idle-symbolic")

        for action in self.actions():
            if Path(os.path.expanduser(action.text())).is_mount():
                action.setIcon(mount)
            else:
                action.setIcon(umount)

    def mount(self, checked, mdir):

        p = Path(mdir)

        if p.is_mount():
            cmd = "umount"
        else:
            cmd = "mount"

        self.parent.showMessage("Attempting to {}...".format(cmd), mdir)

        try:
            m = subprocess.check_call([cmd, mdir])
        except subprocess.CalledProcessError as CPE:
            self.parent.showMessage("Error!", CPE.cmd)

        self.parent.showMessage("Command finished.", 
                "Operation {} on {} finished with {}".format(cmd, mdir, m))

    def xdg_open(self, checked, mdir):
        cmd = "xdg-open"
        subprocess.Popen([cmd, mdir], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


class SystemTrayIcon(QtWidgets.QSystemTrayIcon):
    def __init__(self, parent=None):
        icon = QtGui.QIcon.fromTheme("network-server")
        QtWidgets.QSystemTrayIcon.__init__(self, icon=icon, parent=parent)

        self.right_menu = RightClickMenu(parent=self)
        self.setContextMenu(self.right_menu)

    def welcome(self):
        self.showMessage("sftper", "Up and running!")

    def show(self):
        QtWidgets.QSystemTrayIcon.show(self)
        QtCore.QTimer.singleShot(100, self.welcome)

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    app = QtWidgets.QApplication(sys.argv)
    tray = SystemTrayIcon()
    tray.show()
    sys.exit(app.exec_())
