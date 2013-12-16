#!/usr/bin/python2

import os, ConfigParser

import lib.message as message

if not os.path.isfile('/etc/customizer.conf'):
    message.warning('Configuration file does not exists', '/etc/customizer.comf')

    FILESYSTEM_DIR = "/home/FileSystem"
    ISO_DIR = "/home/ISO"
    MOUNT_DIR = "/media"
    MESSAGES_COLORS = True
    FORCE_CHROOT = True
    LOCALES = "C"
    RESOLUTION = "800x600"
    COMPRESSION = "xz"
    VRAM = "256"
    ISO = ""
    DEB = ""
    HOOK = ""
else:
    conf = ConfigParser.SafeConfigParser()
    conf.read('/etc/customizer.conf')

    FILESYSTEM_DIR = conf.get('main', 'FILESYSTEM_DIR')
    ISO_DIR = conf.get('main', 'ISO_DIR')
    MOUNT_DIR = conf.get('main', 'MOUNT_DIR')

    MESSAGES_COLORS = conf.getboolean('preferences', 'MESSAGES_COLORS')
    FORCE_CHROOT = conf.getboolean('preferences', 'FORCE_CHROOT')
    LOCALES = conf.get('preferences', 'LOCALES')
    RESOLUTION = conf.get('preferences', 'RESOLUTION')
    COMPRESSION = conf.get('preferences', 'COMPRESSION')
    VRAM = conf.get('preferences', 'VRAM')

    ISO = conf.get('saved', 'ISO')
    DEB = conf.get('saved', 'DEB')
    HOOK = conf.get('saved', 'HOOK')
