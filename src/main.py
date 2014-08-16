#!/usr/bin/python2

import sys, ConfigParser, subprocess, shutil, os, re, argparse

import lib.message as message

import actions.extract as extract
import actions.chroot as chroot
import actions.xnest as xnest
import actions.pkgm as pkgm
import actions.deb as deb
import actions.hook as hook
import actions.rebuild as rebuild
import actions.qemu as qemu
import actions.clean as clean

app_version = "4.1.0 (a70719f)"

try:
    class OverrideDebug(argparse.Action):
        def __call__(self, parser, namespace, values, option_string=None):
            message.DEBUG = True
            setattr(namespace, self.dest, values)

    parser = argparse.ArgumentParser(prog='Customizer', \
        description='Ubuntu based LiveCD ISO images remastering tool')

    parser.add_argument('-e', '--extract', action='store_true', \
        help='Exctract ISO image')
    parser.add_argument('-c', '--chroot', action='store_true', \
        help='Chroot into the filesystem')
    parser.add_argument('-x', '--xnest', action='store_true', \
        help='Execute nested X-session')
    parser.add_argument('-p', '--pkgm', action='store_true', \
        help='Execute package manager')
    parser.add_argument('-d', '--deb', action='store_true', \
        help='Install Debian package')
    parser.add_argument('-k', '--hook', action='store_true', \
        help='Execute hook')
    parser.add_argument('-r', '--rebuild', action='store_true', \
        help='Rebuild the ISO image')
    parser.add_argument('-q', '--qemu', action='store_true', \
        help='Test the builded image with QEMU')
    parser.add_argument('-t', '--clean', action='store_true', \
        help='Clean all temporary files and folders')

    parser.add_argument('-D', '--debug', nargs=0, action=OverrideDebug, \
        help='Enable debug messages')
    parser.add_argument('-v', '--version', action='version', \
        version='Customizer v' + app_version, \
        help='Show Customizer version and exit')
    ARGS = parser.parse_args()

    if not os.geteuid() == 0:
        message.critical('You are not root')
        sys.exit(2)

    if ARGS.extract:
        message.info('Extracting...')
        extract.main()

    if ARGS.chroot:
        message.info('Chrooting...')
        chroot.main()

    if ARGS.xnest:
        message.info('Running nested X session...')
        xnest.main()

    if ARGS.pkgm:
        message.info('Running package manager...')
        pkgm.main()

    if ARGS.deb:
        message.info('Installing Debian package...')
        deb.main()

    if ARGS.hook:
        message.info('Running chroot hook...')
        hook.main()


    if ARGS.rebuild:
        message.info('Rebuilding ISO...')
        rebuild.main()

    if ARGS.qemu:
        message.info('Running QEMU...')
        qemu.main()

    if ARGS.clean:
        message.info('Cleaning up...')
        clean.main()

except ConfigParser.Error as detail:
    message.critical('CONFIGPARSER' + str(detail))
    sys.exit(3)
except subprocess.CalledProcessError as detail:
    message.critical('SUBPROCESS: ' + str(detail))
    sys.exit(4)
except shutil.Error as detail:
    message.critical('SHUTIL: ' + str(detail))
    sys.exit(5)
except OSError as detail:
    message.critical('OS: ' + str(detail))
    sys.exit(6)
except IOError as detail:
    message.critical('IO: ' + str(detail))
    sys.exit(7)
except re.error as detail:
    message.critical('REGEXP: ' + str(detail))
    sys.exit(8)
except KeyboardInterrupt:
    message.critical('Interupt signal received')
    sys.exit(9)
except SystemExit:
    sys.exit(2)
except Exception as detail:
    message.critical('Unexpected error', detail)
    sys.exit(1)
#finally:
#    raise
