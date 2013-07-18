#!/usr/bin/python2

import sys, os, shutil, subprocess, hashlib, time

import lib.misc as misc
import lib.configparser as configparser
import lib.message as message

# FIXME: make this common
def search(sfile, string):
	for line in misc.read_file(sfile).split('\n'):
		if line.startswith(string):
			line = line.replace(string, '')
			line = line.replace("'", "")
			line = line.replace('"', '')
			return line


def check():
	corrupted = False
	
	for sdir in ['bin', 'sbin', 'usr/bin', 'usr/sbin', 'etc', 'lib', 'usr/lib']:
			full_dir = misc.join_paths(configparser.FILESYSTEM_DIR, sdir)
			if not os.path.isdir(full_dir):
				corrupted = True
				break
	
	if corrupted:
		message.sub_critical('Filesystem is missing or corrupted')
		sys.exit(2)

def detect_boot():
	global initrd
	global vmlinuz
	
	initrd = None
	vmlinuz = None
	for sfile in misc.list_files(misc.join_paths(configparser.FILESYSTEM_DIR, 'boot')):
		if sfile.startswith(misc.join_paths(configparser.FILESYSTEM_DIR, 'boot/initrd.img')):
			initrd = sfile
		elif sfile.startswith(misc.join_paths(configparser.FILESYSTEM_DIR, 'boot/vmlinuz')):
			vmlinuz = sfile


def main():
	message.sub_info('Checking')
	check()

	message.sub_info('Doing sanity checks')
	lsb_file = misc.join_paths(configparser.FILESYSTEM_DIR, 'etc/lsb-release')
	if not os.path.isfile(lsb_file):
		message.sub_critical(lsb_file + ' does not exists')
		sys.exit(2)
		
	casper_file = misc.join_paths(configparser.FILESYSTEM_DIR, 'etc/casper.conf')
	if not os.path.isfile(casper_file):
		message.sub_critical(casper_file + ' does not exists')
		sys.exit(2)
	
	isolinux_dir = misc.join_paths(configparser.ISO_DIR, 'isolinux')
	if not os.path.isdir(isolinux_dir):
		message.sub_critical(isolinux_dir + ' does not exist')
		sys.exit(2)
	
	disk_dir = misc.join_paths(configparser.ISO_DIR, '.disk')
	if not os.path.isdir(disk_dir):
		os.makedirs(disk_dir)
	
	casper_dir = misc.join_paths(configparser.ISO_DIR, 'casper')
	if not os.path.isdir(casper_dir):
		os.makedirs(casper_dir)

	cd_file = misc.join_paths(disk_dir, 'cd_type')
	if not os.path.isfile(cd_file):
		misc.write_file(cd_file, 'full_cd/single')

	base_file = misc.join_paths(disk_dir, 'base_installable')
	if os.path.isfile(misc.join_paths(configparser.FILESYSTEM_DIR, 'usr/bin/ubiquity')):
		if not os.path.isfile(base_file):
			misc.write_file(base_file, '')
	elif os.path.isfile(base_file):
		os.unlink(base_file)

	uuid_file = misc.join_paths(disk_dir, 'casper-uuid-generic')
	if not os.path.isfile(uuid_file):
		misc.write_file(uuid_file, 'f01d0b93-4f0e-4e95-93ae-e3d0e114d4f7')
	
	url_file = misc.join_paths(disk_dir, 'release_notes_url')
	if not os.path.isfile(url_file):
		misc.write_file(url_file, 'http://www.ubuntu.com/getubuntu/releasenotes')

	message.sub_info('Loading configs')
	arch = misc.chroot_exec(['dpkg', '--print-architecture'], prepare=False, mount=False, output=True)
	distrib = search(configparser.FILESYSTEM_DIR + '/etc/lsb-release', 'DISTRIB_ID=')
	release = search(configparser.FILESYSTEM_DIR + '/etc/lsb-release', 'DISTRIB_RELEASE=')
	codename = search(configparser.FILESYSTEM_DIR + '/etc/lsb-release', 'DISTRIB_CODENAME=')
	username = search(configparser.FILESYSTEM_DIR + '/etc/casper.conf', 'export USERNAME=')

	message.sub_info('Cleaning up')
	for sfile in ['casper/filesystem.squashfs', 'casper/initrd.lz', 'casper/vmlinuz',
		'casper/vmlinuz.efi', 'casper/filesystem.manifest', 'casper/filesystem.manifest-desktop'
		'casper/filesystem.size', 'casper/README.diskdefines' 'md5sum.txt']:
		
		full_file = misc.join_paths(configparser.ISO_DIR, sfile)
		if os.path.exists(full_file):
			os.unlink(full_file)
	
	iso_file = '/home/%s-%s-%s.iso' % (distrib, arch, release)
	if os.path.exists(iso_file):
			os.unlink(iso_file)

	detect_boot()
	if not initrd or not vmlinuz:
		message.sub_info('Purging Kernels (if any)')
		misc.chroot_exec(['apt-get', 'purge', '--yes', 'linux-image*', 'linux-headers*', '-qq'])
		message.sub_info('Installing Kernel')
		misc.chroot_exec(['apt-get', 'install', '--yes', 'linux-image-generic', 'linux-headers-generic', '-qq'])
	else:
		message.sub_info('Updating/creating Kernel images')
		misc.chroot_exec(['update-initramfs', '-k', 'all', '-t', '-u'])

	detect_boot()
	if not initrd or not vmlinuz:
		message.sub_critical('Missing boot file (initrd or vmlinuz)')
		sys.exit(2)
	else:
		misc.copy_file(initrd, misc.join_paths(configparser.ISO_DIR, 'casper/initrd.lz'))
		misc.copy_file(vmlinuz, misc.join_paths(configparser.ISO_DIR, 'casper/vmlinuz'))
		if os.path.isdir(misc.join_paths(configparser.ISO_DIR, 'efi/boot')):
			misc.copy_file(vmlinuz, misc.join_paths(configparser.ISO_DIR, 'casper/vmlinuz.efi'))
	
	if configparser.BOOT_FILES:
		message.sub_info('Deleteing boot files')
		for sfile in misc.list_files(misc.join_paths(configparser.FILESYSTEM_DIR, 'boot')):
			if sfile.startswith(misc.join_paths(configparser.FILESYSTEM_DIR, 'boot/initrd.img')):
				os.unlink(sfile)
			elif sfile.startswith(misc.join_paths(configparser.FILESYSTEM_DIR, 'boot/vmlinuz')):
				os.unlink(sfile)
			elif sfile.startswith(misc.join_paths(configparser.FILESYSTEM_DIR, 'boot/config')):
				os.unlink(sfile)
	
	message.sub_info('Creating squashed FileSystem')
	subprocess.check_call(['mksquashfs', configparser.FILESYSTEM_DIR,
				misc.join_paths(configparser.ISO_DIR, 'casper/filesystem.squashfs'),
				'-wildcards', '-ef', '/usr/share/customizer/exclude.list', '-comp', configparser.COMPRESSION])
	
	message.sub_info('Checking filesystem size')
	fs_size = os.path.getsize(misc.join_paths(configparser.ISO_DIR, 'casper/filesystem.squashfs'))
	if fs_size > 4000000000:
		message.sub_critical('The squashed filesystem size is greater than 4GB')
		sys.exit(2)

	message.sub_info('Creating filesystem.size')
	misc.write_file(misc.join_paths(configparser.ISO_DIR, 'casper/filesystem.size'), str(fs_size))

	message.sub_info('Creating filesystem.manifest')
	packages_list = misc.chroot_exec(["dpkg-query", "-W", "--showformat=${Package} ${Version}\\n"], prepare=False, mount=False, output=True)
	misc.write_file(misc.join_paths(configparser.ISO_DIR, 'casper/filesystem.manifest'), packages_list)

	message.sub_info('Creating filesystem.manifest-desktop')
	for pkg in ['ubiquity', 'casper', 'live-initramfs', 'user-setup', 'discover1', 'xresprobe', 'libdebian-installer4']:
		packages_list.replace(pkg, '')
	misc.write_file(misc.join_paths(configparser.ISO_DIR, 'casper/filesystem.manifest-desktop'), packages_list)
	
	message.sub_info('Creating README.diskdefines')
	misc.write_file(misc.join_paths(configparser.ISO_DIR, 'README.diskdefines'),
'''#define DISKNAME  %s %s "%s" - Release %s
#define TYPE  binary
#define TYPEbinary  1
#define ARCH  $ARCH
#define ARCH$ARCH  1
#define DISKNUM  1
#define DISKNUM1  1
#define TOTALNUM  0
#define TOTALNUM0  1''' % (distrib, release, codename, arch))

	message.sub_info('Creating disk info')
	misc.write_file(misc.join_paths(configparser.ISO_DIR, '.disk/info'), '%s %s "%s" - Release %s (%s)' % (distrib, release, codename, arch, time.strftime('%Y%m%d', time.localtime())))


	message.sub_info('Creating MD5Sums')
	checksum_file = misc.join_paths(configparser.ISO_DIR, 'md5sum.txt')
	misc.write_file(checksum_file, '')
	for sfile in misc.list_files(configparser.ISO_DIR):
		if sfile.endswith('md5sum.txt'):
			continue
		
		# FIXME: read in chunks
		checksum = hashlib.md5(misc.read_file(sfile)).hexdigest()
		misc.append_file(checksum_file, checksum + '  .' + sfile.replace(configparser.ISO_DIR, '') +'\n')

	message.sub_info('Creating ISO')
	os.chdir(configparser.ISO_DIR)
	subprocess.check_call(['xorriso', '-as', 'mkisofs', '-r', '-V', distrib + '-' + arch + '-' + release,
	'-b', 'isolinux/isolinux.bin', '-c', 'isolinux/boot.cat', '-cache-inodes',
	'-J', '-l', '-no-emul-boot', '-boot-load-size', '4', '-boot-info-table',
	'-o', iso_file, '-input-charset', 'utf-8', '.'])
	# chmod 555 "/home/$DIST-$ARCH-$VERSION.iso"

	message.mark_sub_info('Successfuly created ISO image', iso_file)