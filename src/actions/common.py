#!/usr/bin/python2

import sys, os, shutil

import lib.misc as misc
import lib.config as config
import lib.message as message

def check_filesystem():
    message.sub_info('Checking')
    corrupted = False
    for sdir in ('bin', 'sbin', 'usr/bin', 'usr/sbin', 'etc', 'lib', 'usr/lib'):
        full_dir = misc.join_paths(config.FILESYSTEM_DIR, sdir)
        if not os.path.isdir(full_dir):
            corrupted = True
            break

    if corrupted:
        message.sub_critical('Filesystem is missing or corrupted')
        sys.exit(2)

def create_work_dirs():
    if not os.path.isdir(config.FILESYSTEM_DIR):
        message.sub_info('Creating', config.FILESYSTEM_DIR)
        os.makedirs(config.FILESYSTEM_DIR)

    if not os.path.isdir(config.ISO_DIR):
        message.sub_info('Creating', config.ISO_DIR)
        os.makedirs(config.ISO_DIR)

    if not os.path.isdir(config.MOUNT_DIR):
        message.sub_info('Creating', config.MOUNT_DIR)
        os.makedirs(config.MOUNT_DIR)

def clean_work_dirs():
    if os.path.isdir(config.FILESYSTEM_DIR):
        message.sub_info('Removing', config.FILESYSTEM_DIR)
        shutil.rmtree(config.FILESYSTEM_DIR)

    if os.path.isdir(config.ISO_DIR):
        message.sub_info('Removing', config.ISO_DIR)
        shutil.rmtree(config.ISO_DIR)

