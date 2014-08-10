#!/usr/bin/python2

import gui_ui
from PyQt4 import QtCore, QtGui
import sys, os

import lib.message as message
import lib.config as config
import actions.extract as extract
import actions.chroot as chroot
import actions.xnest as xnest
import actions.pkgm as pkgm
import actions.deb as deb
import actions.hook as hook
import actions.rebuild as rebuild
import actions.clean as clean

app_version = "4.1.0 (22b58e5)"

# prepare for lift-off
app = QtGui.QApplication(sys.argv)
MainWindow = QtGui.QMainWindow()
ui = gui_ui.Ui_MainWindow()
ui.setupUi(MainWindow)


def setup_gui():
    ui.WorkDirEdit.setText(config.FILESYSTEM_DIR)
    ui.ISODirEdit.setText(config.ISO_DIR)
    if os.path.isdir(config.FILESYSTEM_DIR):
        #ui.customizationBox.setEnabled(True)
        ui.rebuildButton.setEnabled(True)
        ui.cleanButton.setEnabled(True)
    else:
        #ui.customizationBox.setEnabled(False)
        ui.rebuildButton.setEnabled(False)
        ui.cleanButton.setEnabled(False)

def select_iso():
    sfile = QtGui.QFileDialog.getOpenFileName(MainWindow, 'Open', \
        QtCore.QDir.currentPath(), 'ISO Files (*.iso);;All Files (*)')
    if not sfile:
        return
    sfile = str(sfile)
    # FIXME: make the change permanent
    extract.config.ISO = sfile
    try:
        extract.main()
    except SystemExit:
        # FIXME: set status failed
        pass
    finally:
        setup_gui()

def rebuild_iso():
    try:
        rebuild.main()
    except:
        # FIXME: set status failed
        pass
    finally:
        setup_gui()

def cleanup():
    try:
        clean.main()
    except:
        # FIXME: set status failed
        pass
    finally:
        setup_gui()

ui.aboutLabel.setText('<b>Customizer v' + app_version + '</b>')
ui.selectButton.clicked.connect(select_iso)
ui.rebuildButton.clicked.connect(rebuild_iso)
ui.cleanButton.clicked.connect(cleanup)
setup_gui()

MainWindow.show()
sys.exit(app.exec_())

