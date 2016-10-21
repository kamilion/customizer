#!/usr/bin/python2.7

import os

import lib.misc as misc
import lib.config as config
import lib.message as message
import actions.common as common

def main():
    common.check_filesystem()

    if not os.path.isfile(config.DEB):
        raise(message.exception('DEB does not exists', config.DEB))
    elif not config.DEB.endswith('.deb'):
        raise(message.exception('File is not DEB', config.DEB))

    message.sub_info('Copying DEB file')
    deb_file = misc.join_paths(config.FILESYSTEM_DIR, 'temp.deb')
    if os.path.isfile(deb_file):
        message.sub_debug('Removing', deb_file)
        os.unlink(deb_file)
    misc.copy_file(config.DEB, deb_file)

    try:
        message.sub_info('Installing DEB')
        misc.chroot_exec(('dpkg', '-i', '/temp.deb'))
        message.sub_info('Installing dependencies')
        misc.chroot_exec(('apt-get', 'install', '-f', '-y'))
    finally:
        if os.path.isfile(deb_file):
            os.unlink(deb_file)
