#!/usr/bin/python2

import os
try:  # Importing python3 style first.
    import configparser as ConfigParser
except:  # Fall back to python2.
    import ConfigParser

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
    message.warning('Configuration file does not exist', '/etc/customizer.conf')

conf.read('/etc/customizer.conf')
message.info('Read Configuration file', '/etc/customizer.conf')
for section in ('preferences', 'saved'):
    if not conf.has_section(section):
        conf.add_section(section)

# Make sure these end up to be strings in both python2 and python3.
WORK_DIR = '{}'.format(conf.get('preferences', 'WORK_DIR'))
LOCALES = '{}'.format(conf.get('preferences', 'LOCALES'))
RESOLUTION = '{}'.format(conf.get('preferences', 'RESOLUTION'))
COMPRESSION = '{}'.format(conf.get('preferences', 'COMPRESSION'))
VRAM = '{}'.format(conf.get('preferences', 'VRAM'))

ISO = '{}'.format(conf.get('saved', 'ISO'))
DEB = '{}'.format(conf.get('saved', 'DEB'))
HOOK = '{}'.format(conf.get('saved', 'HOOK'))

MOUNT_DIR = '/media'
FILESYSTEM_DIR = os.path.join(WORK_DIR, 'FileSystem')
ISO_DIR = os.path.join(WORK_DIR, 'ISO')
