#!/usr/bin/env python3

import sys, signal, os, threading, subprocess
import sftper.autostart
from sftper.fstab import Fstab
from time import sleep
from PyQt5 import QtWidgets, QtGui, QtCore
from pathlib import Path

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
                mount_action.triggered.connect(lambda checked, a=str(mdir): self.mount(checked,a))
                fstab_entry.addAction(mount_action)

                open_action = QtWidgets.QAction("Open in file manager", self)
                open_action.triggered.connect(lambda checked, a=mdir: self.xdg_open(checked,a))
                fstab_entry.addAction(open_action)

                self.addMenu(fstab_entry)

    def check_if_mount(self):
        mount = QtGui.QIcon.fromTheme("network-transmit-receive-symbolic")
        umount = QtGui.QIcon.fromTheme("network-idle-symbolic")

        for action in self.actions():
            mdir = Path(os.path.expanduser(action.text()))
            if mdir.is_mount():
                action.setIcon(mount)
                action.menu().actions()[0].setText("Unmount")
            else:
                action.setIcon(umount)
                action.menu().actions()[0].setText("Mount")

    def mount(self, checked, mdir):
        def __mount(mdir):
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

        t = threading.Thread(target=__mount, args=(mdir,))
        t.start()

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

def main():
    if len(sys.argv) > 1:
        if sys.argv[1] == '--autostart':
            autostart.start()
            sys.exit(0)
        elif sys.argv[1] == '--no-autostart':
            autostart.stop()
            sys.exit(0)

    signal.signal(signal.SIGINT, signal.SIG_DFL)
    app = QtWidgets.QApplication(sys.argv)
    tray = SystemTrayIcon()
    tray.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
