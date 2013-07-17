#!/usr/bin/python2

import sys, os, shutil, tempfile, subprocess

import lib.misc as misc
import lib.configparser as configparser
import lib.message as message

def create_work_dirs():
	if not os.path.isdir(configparser.FILESYSTEM_DIR):
		message.mark_sub_info('Creating', configparser.FILESYSTEM_DIR)
		os.makedirs(configparser.FILESYSTEM_DIR)
	
	if not os.path.isdir(configparser.ISO_DIR):
		message.mark_sub_info('Creating', configparser.ISO_DIR)
		os.makedirs(configparser.ISO_DIR)
		
def clean_work_dirs():
	# subprocess.check_call([misc.whereis('umount'), configparser.MOUNT_DIR])
	if os.path.isdir(configparser.FILESYSTEM_DIR):
		message.mark_sub_info('Removing', configparser.FILESYSTEM_DIR)
		shutil.rmtree(configparser.FILESYSTEM_DIR)
	
	if os.path.isdir(configparser.ISO_DIR):
		message.mark_sub_info('Removing', configparser.ISO_DIR)
		shutil.rmtree(configparser.ISO_DIR)
		
def main():
	if not os.path.isfile(configparser.ISO):
		message.mark_sub_critical('ISO does not exists', configparser.ISO)
		sys.exit(2)
	
	clean_work_dirs()
	create_work_dirs()

	message.sub_info('Creating mount dir')
	mount_dir = tempfile.mkdtemp(prefix=configparser.MOUNT_DIR + '/')
	
	message.mark_sub_info('Mounting ISO', configparser.ISO)
	subprocess.check_call([misc.whereis('mount'), '-t', 'iso9660', '-o', 'ro,loop', configparser.ISO, mount_dir])

	message.sub_info('Checking ISO')
	invalid_iso = False
	for sfile in [mount_dir + '/casper/filesystem.squashfs', mount_dir + '/.disk', mount_dir + '/isolinux']:
		if not os.path.exists(sfile):
			invalid_iso = True
			
	if invalid_iso == True:
		message.mark_sub_critical('Invalid ISO', configparser.ISO)
		clean_work_dirs
		sys.exit(2)

	message.sub_info('Unsquashing filesystem')
	subprocess.check_call([misc.whereis('unsquashfs'), '-f', '-d', configparser.FILESYSTEM_DIR, mount_dir + '/casper/filesystem.squashfs'])
	
	message.sub_info('Checking architecture')
	architecture = misc.chroot_exec(['dpkg', '--print-architecture'], output=True)
	if architecture == 'amd64' and not os.uname()[4] == 'x86_64':
		message.sub_critical('The ISOs architecture is amd64 and yours is not')
		clean_work_dirs
		sys.exit(2)

	message.sub_info('Copying ISO files')
	for sfile in misc.list_files(mount_dir):
		if sfile.startswith(mount_dir + '/casper'):
			continue
		elif sfile == mount_dir + '/md5sum.txt' or sfile == mount_dir + '/README.diskdefines':
			continue
		else:
			new_file = sfile.replace(mount_dir, configparser.ISO_DIR)
			new_dir = os.path.dirname(new_file)
			
			if not os.path.isdir(new_dir):
				os.makedirs(new_dir)
				
			shutil.copyfile(sfile, new_file)

	message.mark_sub_info('Unmounting', mount_dir)
	subprocess.check_call([misc.whereis('umount'), mount_dir])
	
	message.mark_sub_info('Removing', mount_dir)
	os.rmdir(mount_dir)
