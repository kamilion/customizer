#!/usr/bin/python2

import sys, os

import lib.misc as misc
import lib.config as config
import lib.message as message
import actions.common as common

def main():
    common.check_filesystem()

    if not os.path.isfile(config.DEB):
        message.sub_critical('DEB does not exists', config.DEB)
        sys.exit(2)
    elif not config.DEB.endswith('.iso'):
        message.sub_critical('File is not DEB', config.DEB)
        sys.exit(2)

    message.sub_info('Copying DEB file')
    deb_file = misc.join_paths(config.FILESYSTEM_DIR, 'temp.deb')
    if os.path.isfile(deb_file):
        os.unlink(deb_file)
    misc.copy_file(config.DEB, deb_file)

    message.sub_info('Installing DEB')
    misc.chroot_exec(['dpkg', '-i', '/temp.deb'])
    message.sub_info('Installing dependencies')
    misc.chroot_exec(['apt-get', 'install', '-f', '-y'])
