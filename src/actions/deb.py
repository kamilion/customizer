#!/usr/bin/python2

import sys, os

import lib.misc as misc
import lib.configparser as configparser
import lib.message as message

def check():
	if not os.path.isfile(configparser.DEB):
		message.mark_sub_critical('DEB does not exists', configparser.DEB)
		sys.exit(2)
	elif not configparser.DEB.endswith('.iso'):
		message.mark_sub_critical('File is not DEB', configparser.DEB)
		sys.exit(2)
		
def main():
	message.sub_info('Checking')
	check()
	
	message.sub_info('Copying DEB file')
	deb_file = misc.join_paths(configparser.FILESYSTEM_DIR, 'temp.deb')
	if os.path.isfile(deb_file):
		os.unlink(deb_file)
	misc.copy_file(configparser.DEB, deb_file)
	
	message.sub_info('Installing DEB')
	misc.chroot_exec(['dpkg', '-i', '/tmp.deb'])
	message.sub_info('Installing dependencies')
	misc.chroot_exec(['apt-get', 'install', '-f', '-y'])
	