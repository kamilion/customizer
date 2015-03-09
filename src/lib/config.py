#!/usr/bin/python2

import os, ConfigParser

import lib.message as message

conf = ConfigParser.SafeConfigParser(
    {
        'WORK_DIR': '/home',
        'LOCALES': 'C',
        'RESOLUTION': '800x600',
        'COMPRESSION': 'xz',
        'VRAM': '256',
        'ISO': '',
        'DEB': '',
        'HOOK': '',
    }
)

if not os.path.isfile('/etc/customizer.conf'):
    message.warning('Configuration file does not exists', '/etc/customizer.conf')

conf.read('/etc/customizer.conf')
for section in ('preferences', 'saved'):
    if not conf.has_section(section):
        conf.add_section(section)

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
