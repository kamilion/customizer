#!/usr/bin/python2

import lib.misc as misc
import lib.message as message
import actions.common as common

def main():
    common.check_filesystem()

    message.sub_info('Chrooting')
    misc.chroot_exec(('bash'))
