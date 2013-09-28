#!/usr/bin/python2

import lib.message as message
import actions.extract as extract

def main():
    message.sub_info('Cleaning')
    extract.clean_work_dirs()
