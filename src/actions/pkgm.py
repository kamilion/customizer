#!/usr/bin/python2

import sys, os

import lib.misc as misc
import lib.configparser as configparser
import lib.message as message

def check():
	global pkgmngr
	corrupted = False
	pkgmngr = None
	
	for sdir in ['bin', 'sbin', 'usr/bin', 'usr/sbin', 'etc', 'lib', 'usr/lib']:
			full_dir = misc.join_paths(configparser.FILESYSTEM_DIR, sdir)
			if not os.path.isdir(full_dir):
				corrupted = True
				break
	
	if corrupted:
		message.sub_critical('Filesystem is missing or corrupted')
		sys.exit(2)
		
	# FIXME: 'synaptic'
	for sfile in ['aptitude', 'aptitude-curses']:
		for sdir in ['bin', 'sbin', 'usr/bin', 'usr/sbin']:
			full_file = misc.join_paths(configparser.FILESYSTEM_DIR, sdir, sfile)
			if os.path.exists(full_file) and os.access(full_file, os.X_OK):
				pkgmngr = misc.join_paths(sdir, sfile)
				
	if not pkgmngr:
		message.sub_critical('No package manager available')
		sys.exit(2)
	
def main():
	message.sub_info('Checking')
	check()
	
	message.sub_info('Executing package manager')
	misc.chroot_exec([pkgmngr])