#!/usr/bin/env python3

import sys, signal
from fstab import Fstab
from time import sleep
from PyQt5 import QtWidgets, QtGui, QtCore

class RightClickMenu(QtWidgets.QMenu):
    def __init__(self, parent=None):
        QtWidgets.QMenu.__init__(self, "Test", parent)

        f = Fstab()
        f.read()

        for line in f.lines:
            if line.dict['fstype'] == 'fuse.sshfs':
                mdir = line.dict['directory']
                item = QtWidgets.QAction("{}".format(mdir), self)
                item.triggered.connect(lambda checked, a=mdir: self.onTriggered(checked,a))
                self.addAction(item)

    def onTriggered(self, checked, mdir):
        print(mdir)
        QtWidgets.QSystemTrayIcon.showMessage("test",mdir)

class SystemTrayIcon(QtWidgets.QSystemTrayIcon):
    def __init__(self, parent=None):
        icon = QtGui.QIcon.fromTheme("network-wired-acquiring")
        QtWidgets.QSystemTrayIcon.__init__(self, icon=icon, parent=parent)
        #self.right_menu = RightClickMenu()
        #self.setContextMenu(self.right_menu)

        self.right_menu = RightClickMenu()
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
