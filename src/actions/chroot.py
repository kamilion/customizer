#!/usr/bin/python2

import sys, os

import lib.misc as misc
import lib.configparser as configparser
import lib.message as message

def check():
    corrupted = False

    for sdir in ['bin', 'sbin', 'usr/bin', 'usr/sbin', 'etc', 'lib', 'usr/lib']:
        full_dir = misc.join_paths(configparser.FILESYSTEM_DIR, sdir)
        if not os.path.isdir(full_dir):
            corrupted = True
            break

    if corrupted:
        message.sub_critical('Filesystem is missing or corrupted')
        sys.exit(2)

def main():
    message.sub_info('Checking')
    check()

    message.sub_info('Chrooting')
    misc.chroot_exec(['bash'])
