#!/usr/bin/python2

import sys

import lib.misc as misc
import lib.config as config
import lib.message as message
import actions.common as common

def main():
    common.check_filesystem()

    message.sub_info('Detecting available sessions')
    xsession = None
    for sfile in misc.list_files(misc.join_paths(config.FILESYSTEM_DIR, \
        'usr/share/xsessions')):
        if sfile.endswith('.desktop'):
            xsession = common.get_value(sfile, 'Exec=')
            message.sub_debug('Session detected', xsession)

    if not xsession:
        message.sub_critical('No session avaialable')
        sys.exit(2)

    # FIXME: race condition between session and Xephyr - if session
    # starts before Xephyr it fails saying it does not find the DISPLAY
    message.sub_info('Starting Xephyr')
    x = subprocess.Popen((misc.whereis('Xephyr'), '-ac', '-screen', \
        config.RESOLUTION, '-br', ':13'))
    x.poll()
    if x.returncode > 0:
        message.sub_critical('Failed to start Xephyr', x.returncode)
        sys.exit(2)

    try:
        message.sub_info('Allwoing local access to X-server')
        misc.system_command((misc.whereis('xhost'), '+local:'))

        message.sub_info('Starting nested X session', xsession)
        misc.chroot_exec((xsession), xnest=True)

        message.sub_info('Blocking local access to X-server')
        misc.system_command((misc.whereis('xhost'), '-local:'))
    finally:
        message.sub_info('Terminating Xephyr')
        x.terminate()
