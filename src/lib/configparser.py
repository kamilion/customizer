#!/usr/bin/python2

import sys
import ConfigParser
import lib.message as message

FILESYSTEM_DIR = "/home/FileSystem"
ISO_DIR = "/home/ISO"
MOUNT_DIR = "/media"
MESSAGES_COLORS = "True"
FORCE_CHROOT = "True"
LOCALES = "C"
CHROOT_HELPER = "True"
RESOLUTION = "800x600"
COMPRESSION = "xz"
BOOT_FILES = "False"
VRAM = "256"
ISO = ""
DEB = ""
HOOK = ""

conf = ConfigParser.SafeConfigParser()

conf.read('/etc/customizer.conf')
FILESYSTEM_DIR = conf.get('main', 'FILESYSTEM_DIR')
ISO_DIR = conf.get('main', 'ISO_DIR')
MOUNT_DIR = conf.get('main', 'MOUNT_DIR')

MESSAGES_COLORS = conf.get('preferences', 'MESSAGES_COLORS')
FORCE_CHROOT = conf.get('preferences', 'FORCE_CHROOT')
LOCALES = conf.get('preferences', 'LOCALES')
CHROOT_HELPER = conf.get('preferences', 'CHROOT_HELPER')
RESOLUTION = conf.get('preferences', 'RESOLUTION')
COMPRESSION = conf.get('preferences', 'COMPRESSION')
BOOT_FILES = conf.get('preferences', 'BOOT_FILES')
VRAM = conf.get('preferences', 'VRAM')

ISO = conf.get('preferences', 'ISO')
DEB = conf.get('preferences', 'DEB')
HOOK = conf.get('preferences', 'HOOK')