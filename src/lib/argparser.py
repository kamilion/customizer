#!/usr/bin/python2

import argparse
import lib.configparser as configparser
import lib.message as message

app_version = "4.0.0"
global ARGS

class OverrideColors(argparse.Action):
     def __call__(self, parser, args, values, option_string=None):
        message.COLORS = False
        setattr(args, self.dest, values)

class OverrideDebug(argparse.Action):
     def __call__(self, parser, args, values, option_string=None):
        message.DEBUG = True
        setattr(args, self.dest, values)

class OverrideTraceback(argparse.Action):
     def __call__(self, parser, args, values, option_string=None):
        message.TRACEBACK = True
        setattr(args, self.dest, values)

parser = argparse.ArgumentParser(prog='Customizer', description='Ubuntu based LiveCD ISO images remastering tool')

parser.add_argument('-e', '--extract', action='store_true', help='Exctract ISO image')
parser.add_argument('-c', '--chroot', action='store_true', help='Chroot into the filesystem')
parser.add_argument('-x', '--xnest', action='store_true', help='Execute nested X-session')
parser.add_argument('-p', '--pkgm', action='store_true', help='Execute package manager')
parser.add_argument('-d', '--deb', action='store_true', help='Install Debian package')
parser.add_argument('-k', '--hook', action='store_true', help='Execute hook')
parser.add_argument('-g', '--gui', action='store_true', help='Install GUI (DE/WM)')
parser.add_argument('-r', '--rebuild', action='store_true', help='Rebuild the ISO image')
parser.add_argument('-q', '--qemu', action='store_true', help='Test the builded image with QEMU')
parser.add_argument('-t', '--clean', action='store_true', help='Clean all temporary files and folders')

parser.add_argument('-D', '--debug',nargs=0, action=OverrideDebug, help='Enable debug messages')
parser.add_argument('-T', '--traceback',nargs=0, action=OverrideTraceback, help='Enable traceback messages')
parser.add_argument('-v', '--version', action='version', version='Customizer v' + app_version, help='Show Customizer version and exits')
ARGS = parser.parse_args()
