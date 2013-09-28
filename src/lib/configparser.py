#!/usr/bin/python2

import os
import ConfigParser
import lib.message as message

FILESYSTEM_DIR = "/home/FileSystem"
ISO_DIR = "/home/ISO"
MOUNT_DIR = "/media"
MESSAGES_COLORS = True
FORCE_CHROOT = True
LOCALES = "C"
CHROOT_HELPER = True
RESOLUTION = "800x600"
COMPRESSION = "xz"
BOOT_FILES = False
VRAM = "256"
ISO = ""
DEB = ""
HOOK = ""

conf = ConfigParser.SafeConfigParser()

if not os.path.isfile('/etc/customizer.conf'):
    message.mark_warning('Configuration file does not exists', '/etc/customizer.comf')
else:
    conf.read('/etc/customizer.conf')
    FILESYSTEM_DIR = conf.get('main', 'FILESYSTEM_DIR')
    ISO_DIR = conf.get('main', 'ISO_DIR')
    MOUNT_DIR = conf.get('main', 'MOUNT_DIR')

    MESSAGES_COLORS = conf.getboolean('preferences', 'MESSAGES_COLORS')
    FORCE_CHROOT = conf.getboolean('preferences', 'FORCE_CHROOT')
    LOCALES = conf.get('preferences', 'LOCALES')
    CHROOT_HELPER = conf.getboolean('preferences', 'CHROOT_HELPER')
    RESOLUTION = conf.get('preferences', 'RESOLUTION')
    COMPRESSION = conf.get('preferences', 'COMPRESSION')
    BOOT_FILES = conf.getboolean('preferences', 'BOOT_FILES')
    VRAM = conf.get('preferences', 'VRAM')

    ISO = conf.get('saved', 'ISO')
    DEB = conf.get('saved', 'DEB')
    HOOK = conf.get('saved', 'HOOK')
