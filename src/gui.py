#!/usr/bin/python2

################# NOTE #################
# This is quick and dirty written GUI! #
############### END NOTE ###############

import gui_ui
from PyQt4 import QtCore, QtGui
import sys, os, subprocess

import lib.message as message
import lib.config as config
import lib.misc as misc
import actions.common as common
import actions.extract as extract
import actions.chroot as chroot
import actions.xnest as xnest
import actions.pkgm as pkgm
import actions.deb as deb
import actions.hook as hook
import actions.rebuild as rebuild
import actions.qemu as qemu
import actions.clean as clean

app_version = "4.1.0 (f9a0d52)"

# prepare for lift-off
app = QtGui.QApplication(sys.argv)
MainWindow = QtGui.QMainWindow()
ui = gui_ui.Ui_MainWindow()
ui.setupUi(MainWindow)


def setup_gui():
    ui.WorkDirEdit.setText(config.FILESYSTEM_DIR)
    ui.ISODirEdit.setText(config.ISO_DIR)
    if os.path.isdir(config.FILESYSTEM_DIR):
        ui.configurationBox.setEnabled(True)
        ui.customizationBox.setEnabled(True)
        ui.rebuildButton.setEnabled(True)
        ui.cleanButton.setEnabled(True)

        ui.userEdit.setText(common.get_value( \
            misc.join_paths(config.FILESYSTEM_DIR, 'etc/casper.conf'), 'export USERNAME='))
        ui.hostnameEdit.setText(common.get_value( \
            misc.join_paths(config.FILESYSTEM_DIR, 'etc/casper.conf'), 'export HOST='))
        common.substitute(misc.join_paths(config.FILESYSTEM_DIR, \
        'etc/casper.conf'), '# export FLAVOUR=.*', 'export FLAVOUR="Custom"')

        ui.pkgmButton.setEnabled(False)
        for sfile in ('aptitude', 'aptitude-curses', 'synaptic'):
            for sdir in ('bin', 'sbin', 'usr/bin', 'usr/sbin'):
                full_file = misc.join_paths(config.FILESYSTEM_DIR, sdir, sfile)
                if os.path.exists(full_file) and os.access(full_file, os.X_OK):
                    ui.pkgmButton.setEnabled(True)

        ui.xnestButton.setEnabled(False)
        for sfile in misc.list_files(misc.join_paths(config.FILESYSTEM_DIR, \
            'usr/share/xsessions')):
            if sfile.endswith('.desktop'):
                ui.xnestButton.setEnabled(True)
    else:
        ui.configurationBox.setEnabled(False)
        ui.customizationBox.setEnabled(False)
        ui.rebuildButton.setEnabled(False)
        ui.cleanButton.setEnabled(False)

def msg_critical(msg):
    QtGui.QMessageBox.critical(MainWindow, 'Critical', msg)

def run_core(args, terminal=True):
    if terminal:
        terminal = None
        for term in ('xterm', 'xfce4-terminal', 'gnome-terminal'):
            spath = misc.whereis(term, False)
            if spath:
                terminal = spath

        if not terminal:
            msg_critical('No supported terminal emulator detected')
            return

    try:
        if terminal:
            subprocess.check_call((terminal, '-e', 'customizer -D ' + args))
        else:
            subprocess.check_call(('customizer', '-D', args))
    except Exception as detail:
        # FIXME: set status failed
        msg_critical(str(detail))
    finally:
        setup_gui()

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
        msg_critical(str(detail))
    finally:
        setup_gui()

def run_rebuild():
    try:
        rebuild.main()
    except Exception as detail:
        # FIXME: set status failed
        msg_critical(str(detail))
    finally:
        setup_gui()

def run_clean():
    try:
        clean.main()
    except Exception as detail:
        # FIXME: set status failed
        msg_critical(str(detail))
    finally:
        setup_gui()

def edit_sources():
    editor = None
    for edit in ('leafpad', 'mousepad', 'medit', 'gedit'):
        spath = misc.whereis(edit, False)
        if spath:
            editor = spath

    if not editor:
        msg_critical('No supported text editor detected')
        return

    try:
        subprocess.check_call((editor, misc.join_paths(config.FILESYSTEM_DIR, \
            'etc/apt/sources.list')))
    except Exception as detail:
        # FIXME: set status failed
        msg_critical(str(detail))
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
        msg_critical(str(detail))
    finally:
        setup_gui()

def run_pkgm():
    run_core('-p')

def run_hook():
    sfile = QtGui.QFileDialog.getOpenFileName(MainWindow, 'Open', \
        QtCore.QDir.currentPath(), 'Shell Scripts (*.sh);;All Files (*)')
    if not sfile:
        return
    sfile = str(sfile)
    # FIXME: make the change permanent
    hook.config.HOOK = sfile
    try:
        hook.main()
    except Exception as detail:
        # FIXME: set status failed
        msg_critical(str(detail))
    finally:
        setup_gui()

def run_chroot():
    run_core('-c')

def run_xnest():
    run_core('-x', False)

def change_user():
    common.set_value(misc.join_paths(config.FILESYSTEM_DIR, \
        'etc/casper.conf'), 'export USERNAME=', str(ui.userEdit.text()))

def change_hostname():
    common.set_value(misc.join_paths(config.FILESYSTEM_DIR, \
        'etc/casper.conf'), 'export HOST=', str(ui.hostnameEdit.text()))


ui.aboutLabel.setText('<b>Customizer v' + app_version + '</b>')
ui.selectButton.clicked.connect(run_extract)
ui.rebuildButton.clicked.connect(run_rebuild)
ui.cleanButton.clicked.connect(run_clean)
ui.sourcesButton.clicked.connect(edit_sources)
ui.debButton.clicked.connect(run_deb)
ui.pkgmButton.clicked.connect(run_pkgm)
ui.hookButton.clicked.connect(run_hook)
ui.chrootButton.clicked.connect(run_chroot)
ui.xnestButton.clicked.connect(run_xnest)
ui.userEdit.textChanged.connect(change_user)
ui.hostnameEdit.textEdited.connect(change_hostname)
setup_gui()

MainWindow.show()
sys.exit(app.exec_())
