#!/usr/bin/python2

################# NOTE #################
# This is quick and dirty written GUI! #
############### END NOTE ###############

import gui_ui
from PyQt4 import QtCore, QtGui
import sys, os, atexit, subprocess

import lib.config as config
import lib.misc as misc
import actions.common as common
import actions.extract as extract
import actions.deb as deb
import actions.hook as hook
import actions.rebuild as rebuild
import actions.clean as clean
misc.CATCH = True

app_version = "4.1.0 (ea5d850)"

# prepare for lift-off
app = QtGui.QApplication(sys.argv)
MainWindow = QtGui.QMainWindow()
ui = gui_ui.Ui_MainWindow()
ui.setupUi(MainWindow)

def msg_info(msg):
    QtGui.QMessageBox.information(MainWindow, 'Information', msg)

def msg_warning(msg):
    QtGui.QMessageBox.warning(MainWindow, 'Warning', msg)

def msg_critical(msg):
    QtGui.QMessageBox.critical(MainWindow, 'Critical', msg)

# limit instances to one
lock = '/run/lock/customizer'
running = False
def remove_lock():
    if not running:
        return
    if os.path.isfile(lock):
        os.remove(lock)
atexit.register(remove_lock)

if os.path.isfile(lock):
    msg_critical('An instance of Customizer is already running.')
    sys.exit()
else:
    misc.write_file(lock, str(app.applicationPid()))
    running = True

if int(sys.version_info[0]) >= 3:
    msg_critical('You are attempting to run Customizer with Python 3.')
    sys.exit()

class Thread(QtCore.QThread):
    ''' Worker thread '''
    def __init__(self, func):
        super(Thread, self).__init__()
        self.func = func

    def run(self):
        try:
            self.func()
        except SystemExit:
            pass
        except Exception as detail:
            self.emit(QtCore.SIGNAL('failed'), str(detail))
            self.quit()
        finally:
            self.finished.emit()

def setup_gui():
    locales_file = misc.join_paths(config.FILESYSTEM_DIR, \
        'usr/share/i18n/SUPPORTED')
    if os.path.isfile(locales_file):
        for line in misc.readlines_file(locales_file):
            if not line or not line.startswith('#'):
                ui.localesBox.addItem(line.split(' ')[0])
    ui.qemuButton.setEnabled(False)
    ui.workDirEdit.setText(config.WORK_DIR)
    ui.forceChrootBox.setChecked(config.FORCE_CHROOT)
    index = ui.localesBox.findText(config.LOCALES)
    ui.localesBox.setCurrentIndex(index)
    index = ui.resolutionBox.findText(config.RESOLUTION)
    ui.resolutionBox.setCurrentIndex(index)
    index = ui.vramBox.findText(config.VRAM)
    ui.vramBox.setCurrentIndex(index)
    index = ui.compressionBox.findText(config.COMPRESSION)
    ui.compressionBox.setCurrentIndex(index)
    casper = misc.join_paths(config.FILESYSTEM_DIR, 'etc/casper.conf')
    if os.path.isdir(config.FILESYSTEM_DIR) \
        and os.path.exists(casper):
        ui.changeWorkDirButton.setEnabled(False)
        ui.configurationBox.setEnabled(True)
        ui.customizationBox.setEnabled(True)
        ui.rebuildButton.setEnabled(True)
        ui.cleanButton.setEnabled(True)

        ui.userEdit.setText(common.get_value(casper, 'export USERNAME='))
        ui.hostnameEdit.setText(common.get_value(casper, 'export HOST='))
        common.substitute(casper, '# export FLAVOUR=.*', \
            'export FLAVOUR="Custom"')

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

        arch = misc.chroot_exec(('dpkg', '--print-architecture'), \
            prepare=False, mount=False, output=True)
        distrib = common.get_value(config.FILESYSTEM_DIR + '/etc/lsb-release', \
            'DISTRIB_ID=')
        release = common.get_value(config.FILESYSTEM_DIR + '/etc/lsb-release', \
            'DISTRIB_RELEASE=')
        if os.path.exists('%s/%s-%s-%s.iso' % \
            (config.WORK_DIR, distrib, arch, release)):
            ui.qemuButton.setEnabled(True)
    elif os.path.isdir(config.FILESYSTEM_DIR):
        msg_warning('The filesystem is not valid or corrupted. Clean is recommended.')
        ui.cleanButton.setEnabled(True)
    else:
        ui.changeWorkDirButton.setEnabled(True)
        ui.configurationBox.setEnabled(False)
        ui.customizationBox.setEnabled(False)
        ui.rebuildButton.setEnabled(False)
        ui.cleanButton.setEnabled(False)

def run_core(args, terminal=True):
    if terminal:
        terminal = None
        for term in ('xterm', 'lxterminal', 'xfce4-terminal', \
            'mate-terminal', 'gnome-terminal', 'konsole'):
            spath = misc.whereis(term)
            if spath:
                terminal = spath

        if not terminal:
            msg_critical('No supported terminal emulator detected.')
            return

    try:
        if terminal:
            subprocess.check_call((terminal, '-e', 'customizer -D ' + args))
        else:
            subprocess.check_call((misc.whereis('customizer'), '-D', args))
    except Exception as detail:
        msg_critical(str(detail))
    finally:
        setup_gui()

def change_value(sec, var, val):
    conf = None
    try:
        conf = open('/etc/customizer.conf', 'w')
        if not config.conf.has_section(sec):
            config.conf.add_section(sec)
        config.conf.set(sec, var, val)
        config.conf.write(conf)
    except Exception as detail:
        msg_critical(str(detail))
    finally:
        if conf:
            conf.close()
        reload(config)

def worker_started():
    ui.progressBar.setRange(0, 0)
    ui.progressBar.show()
    ui.changeWorkDirButton.setEnabled(False)
    ui.configurationBox.setEnabled(False)
    ui.customizationBox.setEnabled(False)
    ui.selectButton.setEnabled(False)
    ui.rebuildButton.setEnabled(False)
    ui.qemuButton.setEnabled(False)
    ui.cleanButton.setEnabled(False)

def worker_stopped():
    ui.progressBar.setRange(0, 1)
    ui.progressBar.hide()
    ui.selectButton.setEnabled(True)
    setup_gui()

def worker(func):
    # prevent the thread being destroyed
    global thread
    thread = Thread(func)
    thread.finished.connect(worker_stopped)
    app.connect(thread, QtCore.SIGNAL('failed'), msg_critical)
    worker_started()
    thread.start()

def run_extract():
    sfile = QtGui.QFileDialog.getOpenFileName(MainWindow, 'Open', \
        config.ISO, 'ISO Files (*.iso);;All Files (*)')
    if not sfile:
        return
    sfile = str(sfile)
    change_value('saved', 'iso', sfile)
    extract.config.ISO = sfile
    try:
        worker(extract.main)
    except Exception as detail:
        msg_critical(str(detail))

def run_rebuild():
    try:
        worker(rebuild.main)
    except Exception as detail:
        msg_critical(str(detail))

def run_clean():
    try:
        worker(clean.main)
    except Exception as detail:
        msg_critical(str(detail))

def edit_sources():
    editor = None
    for edit in ('mousepad', 'leafpad', 'pluma', 'gedit', 'kate', 'kwrite', \
        'medit'):
        spath = misc.whereis(edit, False)
        if spath:
            editor = spath

    if not editor:
        msg_critical('No supported text editor detected.')
        return

    try:
        subprocess.check_call((editor, misc.join_paths(config.FILESYSTEM_DIR, \
            'etc/apt/sources.list')))
    except Exception as detail:
        msg_critical(str(detail))
    finally:
        setup_gui()

def run_deb():
    sfile = QtGui.QFileDialog.getOpenFileName(MainWindow, 'Open', \
        config.DEB, 'Deb Files (*.deb);;All Files (*)')
    if not sfile:
        return
    sfile = str(sfile)
    change_value('saved', 'deb', sfile)
    deb.config.DEB = sfile
    try:
        worker(deb.main)
    except Exception as detail:
        msg_critical(str(detail))

def run_pkgm():
    run_core('-p')

def run_hook():
    sfile = QtGui.QFileDialog.getOpenFileName(MainWindow, 'Open', \
        config.HOOK, 'Shell Scripts (*.sh);;All Files (*)')
    if not sfile:
        return
    sfile = str(sfile)
    change_value('saved', 'hook', sfile)
    hook.config.HOOK = sfile
    try:
        worker(hook.main)
    except Exception as detail:
        msg_critical(str(detail))

def run_chroot():
    run_core('-c')

def run_xnest():
    run_core('-x', False)

def run_qemu():
    run_core('-q', False)

def change_user():
    common.set_value(misc.join_paths(config.FILESYSTEM_DIR, \
        'etc/casper.conf'), 'export USERNAME=', str(ui.userEdit.text()))

def change_hostname():
    common.set_value(misc.join_paths(config.FILESYSTEM_DIR, \
        'etc/casper.conf'), 'export HOST=', str(ui.hostnameEdit.text()))

def change_work_dir():
    spath = QtGui.QFileDialog.getExistingDirectory(MainWindow, \
        'Directory', config.WORK_DIR)
    if not spath:
        return
    spath = str(spath)
    change_value('preferences', 'work_dir', spath)
    ui.workDirEdit.setText(spath)

def change_force_chroot():
    current = str(ui.forceChrootBox.isChecked())
    change_value('preferences', 'force_chroot', current)

def change_locales():
    current = str(ui.localesBox.currentText())
    change_value('preferences', 'locales', current)

def change_resolution():
    current = str(ui.resolutionBox.currentText())
    change_value('preferences', 'resolution', current)

def change_vram():
    current = str(ui.vramBox.currentText())
    change_value('preferences', 'vram', current)

def change_compression():
    current = str(ui.compressionBox.currentText())
    change_value('preferences', 'compression', current)

ui.progressBar.hide()
ui.aboutLabel.setText('<b>Customizer v' + app_version + '</b>')
ui.selectButton.clicked.connect(run_extract)
ui.rebuildButton.clicked.connect(run_rebuild)
ui.qemuButton.clicked.connect(run_qemu)
ui.cleanButton.clicked.connect(run_clean)
ui.sourcesButton.clicked.connect(edit_sources)
ui.debButton.clicked.connect(run_deb)
ui.pkgmButton.clicked.connect(run_pkgm)
ui.hookButton.clicked.connect(run_hook)
ui.chrootButton.clicked.connect(run_chroot)
ui.xnestButton.clicked.connect(run_xnest)
ui.userEdit.textChanged.connect(change_user)
ui.hostnameEdit.textEdited.connect(change_hostname)
ui.changeWorkDirButton.clicked.connect(change_work_dir)
ui.forceChrootBox.stateChanged.connect(change_force_chroot)
ui.localesBox.currentIndexChanged.connect(change_locales)
ui.resolutionBox.currentIndexChanged.connect(change_resolution)
ui.vramBox.currentIndexChanged.connect(change_vram)
ui.compressionBox.currentIndexChanged.connect(change_compression)
setup_gui()

MainWindow.show()
sys.exit(app.exec_())
