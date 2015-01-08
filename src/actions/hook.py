#!/usr/bin/python2

import sys, os, stat

import lib.misc as misc
import lib.config as config
import lib.message as message
import actions.common as common

def main():
    common.check_filesystem()

    if not os.path.isfile(config.HOOK):
        raise(message.exception('HOOK does not exists', config.HOOK))

    message.sub_info('Copying HOOK file')
    hook_file = misc.join_paths(config.FILESYSTEM_DIR, 'hook')
    if os.path.isfile(hook_file):
        message.sub_debug('Removing', hook_file)
        os.unlink(hook_file)
    misc.copy_file(config.HOOK, hook_file)

    message.sub_info('Making HOOK executable')
    os.chmod(hook_file, stat.S_IEXEC)

    message.sub_info('Running HOOK')
    misc.chroot_exec(('/hook'))
