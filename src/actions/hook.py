#!/usr/bin/python2

import sys, os, stat

import lib.misc as misc
import lib.configparser as configparser
import lib.message as message

def check():
    if not os.path.isfile(configparser.HOOK):
        message.mark_sub_critical('HOOK does not exists', configparser.HOOK)
        sys.exit(2)

def main():
    message.sub_info('Checking')
    check()

    message.sub_info('Copying HOOK file')
    hook_file = misc.join_paths(configparser.FILESYSTEM_DIR, 'hook')
    if os.path.isfile(hook_file):
        os.unlink(hook_file)
    misc.copy_file(configparser.HOOK, hook_file)

    message.sub_info('Making HOOK executable')
    os.chmod(hook_file, stat.S_IEXEC)

    message.sub_info('Running HOOK')
    misc.chroot_exec(['exec', '/hook'])
