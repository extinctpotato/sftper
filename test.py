#!/usr/bin/env python3

import sys, signal
from fstab import Fstab
from time import sleep
from PyQt5 import QtWidgets, QtGui, QtCore
from pathlib import Path
import subprocess

class RightClickMenu(QtWidgets.QMenu):
    def __init__(self, parent=None):
        QtWidgets.QMenu.__init__(self, "Test", parent=None)
        icon = QtGui.QIcon.fromTheme("drive-removable-media")
        self.parent = parent

        f = Fstab()
        f.read()

        for line in f.lines:
            if line.dict['fstype'] == 'fuse.sshfs':
                mdir = line.dict['directory']
                item = QtWidgets.QMenu("{}".format(mdir), self)
                m = QtWidgets.QAction("Mount", self)
                m.triggered.connect(lambda checked, a=mdir: self.mount(checked,a))
                o = QtWidgets.QAction("Open in file manager", self)
                o.triggered.connect(lambda checked, a=mdir: self.xdg_open(checked,a))
                item.setIcon(icon)
                item.addAction(m)
                item.addAction(o)
                self.addMenu(item)

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
        icon = QtGui.QIcon.fromTheme("network-wired-acquiring")
        QtWidgets.QSystemTrayIcon.__init__(self, icon=icon, parent=parent)
        #self.right_menu = RightClickMenu()
        #self.setContextMenu(self.right_menu)

        self.right_menu = RightClickMenu(parent=self)
        self.setContextMenu(self.right_menu)

        #self.activated.connect(self.click_trap)

    def click_trap(self, value):
        if value == self.Trigger:  # left click!
            self.left_menu.exec_(QtGui.QCursor.pos())

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
