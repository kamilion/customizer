#!/usr/bin/python2

import sys, os, subprocess

import lib.misc as misc
import lib.config as config
import lib.message as message
import actions.common as common

def main():
    common.check_filesystem()

    message.sub_info('Gathering information')
    arch = misc.chroot_exec(('dpkg', '--print-architecture'), prepare=False, \
        mount=False, output=True)
    distrib = common.get_value(config.FILESYSTEM_DIR + '/etc/lsb-release', \
        'DISTRIB_ID=')
    release = common.get_value(config.FILESYSTEM_DIR + '/etc/lsb-release', \
        'DISTRIB_RELEASE=')
    message.sub_debug('Architecture', arch)
    message.sub_debug('Distribution (DISTRIB_ID)', distrib)
    message.sub_debug('Release (DISTRIB_RELEASE)', release)

    iso_file = '/home/%s-%s-%s.iso' % (distrib, arch, release)
    if not os.path.exists(iso_file):
        message.sub_critical('ISO Image does not exists', iso_file)
        sys.exit(2)

    message.sub_info('Running QEMU with ISO image', iso_file)
    host_arch = os.uname()[4]
    message.sub_debug('Host architecture', host_arch)
    if host_arch == 'x86_64':
        subprocess.check_call((misc.whereis('qemu-system-x86_64'), '-m', config.VRAM, '-cdrom', iso_file))
    else:
        subprocess.check_call((misc.whereis('qemu-system-i386'), '-m', config.VRAM, '-cdrom', iso_file))
