#!/usr/bin/python2

import sys, os

import lib.misc as misc
import lib.config as config
import lib.message as message
import actions.common as common

def main():
    common.check_filesystem()

    pkgmngr = None
    # FIXME: 'synaptic'
    for sfile in ['aptitude', 'aptitude-curses']:
        for sdir in ['bin', 'sbin', 'usr/bin', 'usr/sbin']:
            full_file = misc.join_paths(config.FILESYSTEM_DIR, sdir, sfile)
            if os.path.exists(full_file) and os.access(full_file, os.X_OK):
                pkgmngr = misc.join_paths(sdir, sfile)

    if not pkgmngr:
        message.sub_critical('No package manager available')
        sys.exit(2)

    message.sub_info('Executing package manager')
    misc.chroot_exec((pkgmngr))
