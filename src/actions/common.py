#!/usr/bin/python2

import os, re, shutil

import lib.misc as misc
import lib.config as config
import lib.message as message

def check_filesystem():
    message.sub_info('Checking')
    corrupted = False
    for sdir in ('bin', 'sbin', 'usr/bin', 'usr/sbin', 'etc', 'lib', 'usr/lib'):
        full_dir = misc.join_paths(config.FILESYSTEM_DIR, sdir)
        if not os.path.isdir(full_dir):
            message.sub_debug('Non-existing path', full_dir)
            corrupted = True
            break

    if corrupted:
        raise(message.exception('Filesystem is missing or corrupted'))

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
    # ensure that nothing is mounted to the working directories before cleanup,
    # see https://github.com/clearkimura/Customizer/issues/82
    if os.path.exists('/proc/mounts'):
        for line in misc.readlines_file('/proc/mounts'):
            # spaces are recorded as "\\040", handle them unconditionally
            # TODO: test if this actually works with special characters
            mpoint = line.split()[1].replace('\\040', ' ')
            if mpoint.startswith((config.FILESYSTEM_DIR, config.ISO_DIR)):
                message.sub_info('Unmounting', mpoint)
                misc.system_command((misc.whereis('umount'), '-f', '-l', mpoint))
    else:
        message.sub_debug('/proc/mounts does not exists!')

    if os.path.isdir(config.FILESYSTEM_DIR):
        message.sub_info('Removing', config.FILESYSTEM_DIR)
        shutil.rmtree(config.FILESYSTEM_DIR)

    if os.path.isdir(config.ISO_DIR):
        message.sub_info('Removing', config.ISO_DIR)
        shutil.rmtree(config.ISO_DIR)

def get_value(sfile, string):
    for line in misc.readlines_file(sfile):
        if line.startswith(string):
            line = line.replace(string, '')
            line = line.replace("'", "")
            line = line.replace('"', '')
            return line.strip()
    return ''

def set_value(sfile, string, value):
    substitute(sfile, '\\s' + string + '.*\\s', '\n' + string + '"' + value + '"\n')

def substitute(sfile, regex, string):
    content = misc.read_file(sfile)
    new_content = re.sub(regex, string, content)
    misc.write_file(sfile, new_content)
