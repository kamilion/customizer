#!/usr/bin/python2

import sys, subprocess

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
            for sline in misc.readlines_file(sfile):
                if sline.startswith('Exec='):
                    xsession = sline.replace('Exec=', '').strip()
                    message.sub_debug('xsession', xsession)

    if not xsession:
        message.sub_critical('No session avaialable')
        sys.exit(2)

    message.sub_info('Starting Xephyr')
    x = subprocess.Popen(('Xephyr', '-ac', '-screen', config.RESOLUTION, \
        '-br', ':13'))
    x.poll()
    if x.returncode > 0:
        message.sub_critical('Failed to start Xephyr', x.returncode)
        sys.exit(2)

    message.sub_info('Allwoing local access to X-server')
    subprocess.check_call(('xhost', '+local:'))

    message.sub_info('Starting nested X session')
    misc.chroot_exec((xsession), xnest=True)

    message.sub_info('Blocking local access to X-server')
    subprocess.check_call(('xhost', '-local:'))

    message.sub_info('Terminating Xephyr')
    x.terminate()
