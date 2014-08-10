#!/usr/bin/python2

import gui_ui
from PyQt4 import QtCore, QtGui
import sys, os, subprocess

import lib.message as message
import lib.config as config
import lib.misc as misc
import actions.extract as extract
import actions.chroot as chroot
import actions.xnest as xnest
import actions.pkgm as pkgm
import actions.deb as deb
import actions.hook as hook
import actions.rebuild as rebuild
import actions.qemu as qemu
import actions.clean as clean

app_version = "4.1.0 (03eabeb)"

# prepare for lift-off
app = QtGui.QApplication(sys.argv)
MainWindow = QtGui.QMainWindow()
ui = gui_ui.Ui_MainWindow()
ui.setupUi(MainWindow)


def setup_gui():
    ui.WorkDirEdit.setText(config.FILESYSTEM_DIR)
    ui.ISODirEdit.setText(config.ISO_DIR)
    if os.path.isdir(config.FILESYSTEM_DIR):
        ui.customizationBox.setEnabled(True)
        ui.rebuildButton.setEnabled(True)
        ui.cleanButton.setEnabled(True)
    else:
        ui.customizationBox.setEnabled(False)
        ui.rebuildButton.setEnabled(False)
        ui.cleanButton.setEnabled(False)

def run_extract():
    sfile = QtGui.QFileDialog.getOpenFileName(MainWindow, 'Open', \
        QtCore.QDir.currentPath(), 'ISO Files (*.iso);;All Files (*)')
    if not sfile:
        return
    sfile = str(sfile)
    # FIXME: make the change permanent
    extract.config.ISO = sfile
    try:
        extract.main()
    except Exception as detail:
        # FIXME: set status failed
        print(detail)
    finally:
        setup_gui()

def run_rebuild():
    try:
        rebuild.main()
    except Exception as detail:
        # FIXME: set status failed
        print(detail)
    finally:
        setup_gui()

def run_clean():
    try:
        clean.main()
    except Exception as detail:
        # FIXME: set status failed
        print(detail)
    finally:
        setup_gui()

def edit_sources():
    editor = None
    for edit in ('leafpad', 'mousepad', 'medit', 'gedit'):
        spath = misc.whereis(edit, False)
        if spath:
            editor = spath

    if not editor:
        QtGui.QMessageBox.critical(MainWindow, 'Critical', \
            'No supported text editor detected')
        return

    try:
        subprocess.check_call((editor, misc.join_paths(config.FILESYSTEM_DIR, \
            'etc/apt/sources.list')))
    except Exception as detail:
        # FIXME: set status failed
        print(detail)
    finally:
        setup_gui()

def run_deb():
    sfile = QtGui.QFileDialog.getOpenFileName(MainWindow, 'Open', \
        QtCore.QDir.currentPath(), 'Deb Files (*.deb);;All Files (*)')
    if not sfile:
        return
    sfile = str(sfile)
    # FIXME: make the change permanent
    deb.config.DEB = sfile
    try:
        deb.main()
    except Exception as detail:
        # FIXME: set status failed
        print(detail)
    finally:
        setup_gui()


ui.aboutLabel.setText('<b>Customizer v' + app_version + '</b>')
ui.selectButton.clicked.connect(run_extract)
ui.rebuildButton.clicked.connect(run_rebuild)
ui.cleanButton.clicked.connect(run_clean)
ui.sourcesButton.clicked.connect(edit_sources)
ui.debButton.clicked.connect(run_deb)
setup_gui()

MainWindow.show()
sys.exit(app.exec_())

