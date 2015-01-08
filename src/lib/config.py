#!/usr/bin/python2

import os, ConfigParser

import lib.message as message

conf = ConfigParser.SafeConfigParser()
# FIXME: do not assume that the config has all sections and options set
if not os.path.isfile('/etc/customizer.conf'):
    message.warning('Configuration file does not exists', '/etc/customizer.conf')

    WORK_DIR = '/home'
    LOCALES = 'C'
    RESOLUTION = '800x600'
    COMPRESSION = 'xz'
    VRAM = '256'
    ISO = ''
    DEB = ''
    HOOK = ''
else:
    conf.read('/etc/customizer.conf')

    WORK_DIR = conf.get('preferences', 'WORK_DIR')
    LOCALES = conf.get('preferences', 'LOCALES')
    RESOLUTION = conf.get('preferences', 'RESOLUTION')
    COMPRESSION = conf.get('preferences', 'COMPRESSION')
    VRAM = conf.get('preferences', 'VRAM')

    ISO = conf.get('saved', 'ISO')
    DEB = conf.get('saved', 'DEB')
    HOOK = conf.get('saved', 'HOOK')

MOUNT_DIR = '/media'
FILESYSTEM_DIR = os.path.join(WORK_DIR, 'FileSystem')
ISO_DIR = os.path.join(WORK_DIR, 'ISO')
