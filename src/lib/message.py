#!/usr/bin/python2

import sys, os

COLORS = False
DEBUG = False

for handle in [sys.stdout, sys.stderr]:
    if (hasattr(handle, "isatty") and handle.isatty()) or ('TERM' in os.environ and os.environ['TERM']=='ANSI'):
        COLORS = True

if COLORS:
    color_info = '\033[1;32m'
    color_warning = '\033[1;33m'
    color_critical = '\033[1;31m'
    color_debug = '\033[1;36m'
    color_normal = '\033[0m'
else:
    color_info = ''
    color_warning = ''
    color_critical = ''
    color_debug = ''
    color_normal = ''

def info(msg):
    ''' Prints out a message with an INFO status '''
    msg = str(msg)
    print(color_info + "* " + color_normal + msg)

def warning(msg):
    ''' Prints out a message with an WARNING status '''
    msg = str(msg)
    print(color_warning + "* " + color_normal + msg)

def critical(msg):
    ''' Prints out a message with an CRITICAL status '''
    msg = str(msg)
    print(color_critical + "* " + color_normal + msg)

def debug(msg):
    if DEBUG:
        ''' Prints out a message with an DEBUG status '''
        msg = str(msg)
        print(color_debug + "* " + color_normal + msg)

def mark_info(msg, marker):
    ''' Prints out a message with an INFO status and extra marker '''
    msg = str(msg)
    marker = str(marker)
    print(color_info + "* " + color_normal + msg + ": " + color_info + marker + color_normal)

def mark_warning(msg, marker):
    ''' Prints out a message with an WARNING status and extra marker '''
    msg = str(msg)
    marker = str(marker)
    print(color_warning + "* " + color_normal + msg + ": " + color_warning + marker + color_normal)

def mark_critical(msg, marker):
    ''' Prints out a message with an CRITICAL status and extra marker '''
    msg = str(msg)
    marker = str(marker)
    print(color_critical + "* " + color_normal + msg + ": " + color_critical + marker + color_normal)

def mark_debug(msg, marker):
    if DEBUG:
        ''' Prints out a message with an DEBUG status and extra marker '''
        msg = str(msg)
        marker = str(marker)
        print(color_debug + "* " + color_normal + msg + ": " + color_debug + marker + color_normal)
        

def sub_info(msg):
    ''' Prints out a sub-message with an INFO status '''
    msg = str(msg)
    print(color_info + "  => " + color_normal + msg)

def sub_warning(msg):
    ''' Prints out a sub-message with an WARNING status '''
    msg = str(msg)
    print(color_warning + "  => " + color_normal + msg)

def sub_critical(msg):
    ''' Prints out a sub-message with an CRITICAL status '''
    msg = str(msg)
    print(color_critical + "  => " + color_normal + msg)

def sub_debug(msg):
    if DEBUG:
        ''' Prints out a sub-message with an DEBUG status '''
        msg = str(msg)
        print(color_debug + "  => " + color_normal + msg)

def mark_sub_info(msg, marker):
    ''' Prints out a sub-message with an INFO status and extra marker '''
    msg = str(msg)
    marker = str(marker)
    print(color_info + "  => " + color_normal + msg + ": " + color_info + marker + color_normal)

def mark_sub_warning(msg, marker):
    ''' Prints out a sub-message with an WARNING status and extra marker '''
    msg = str(msg)
    marker = str(marker)
    print(color_warning + "  => " + color_normal + msg + ": " + color_warning + marker + color_normal)

def mark_sub_critical(msg, marker):
    ''' Prints out a sub-message with an CRITICAL status and extra marker'''
    msg = str(msg)
    marker = str(marker)
    print(color_critical + "  => " + color_normal + msg + ": " + color_critical + marker + color_normal)

def mark_sub_debug(msg, marker):
    if DEBUG:
        ''' Prints out a sub-message with an DEBUG status and extra marker'''
        msg = str(msg)
        marker = str(marker)
        print(color_debug + "  => " + color_normal + msg + ": " + color_debug + marker + color_normal)
