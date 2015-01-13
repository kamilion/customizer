#!/usr/bin/python2

import sys, os

import lib.misc as misc
import lib.config as config
import lib.message as message
import actions.common as common

def main():
    common.check_filesystem()

    pkgmngr = None
    for sfile in ('aptitude', 'aptitude-curses', 'synaptic', 'apper'):
        for sdir in ('bin', 'sbin', 'usr/bin', 'usr/sbin'):
            full_file = misc.join_paths(config.FILESYSTEM_DIR, sdir, sfile)
            if os.path.exists(full_file) and os.access(full_file, os.X_OK):
                pkgmngr = misc.join_paths(sdir, sfile)
                message.sub_debug('Package manager detected', sfile)

    if not pkgmngr:
        raise(message.exception('No package manager available'))

    if not pkgmngr.startswith('aptitude'):
        try:
            message.sub_info('Allwoing local access to X-server')
            misc.system_command((misc.whereis('xhost'), '+local:'))

            message.sub_info('Executing package manager')
            misc.chroot_exec((pkgmngr))

        finally:
            message.sub_info('Blocking local access to X-server')
            misc.system_command((misc.whereis('xhost'), '-local:'))
    else:
        message.sub_info('Executing package manager')
        misc.chroot_exec((pkgmngr))
