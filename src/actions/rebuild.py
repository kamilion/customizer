#!/usr/bin/python2

import sys, os, subprocess, hashlib, time

import lib.misc as misc
import lib.config as config
import lib.message as message
import actions.common as common

# FIXME: make this common
def search(sfile, string):
    for line in misc.read_file(sfile).split('\n'):
        if line.startswith(string):
            line = line.replace(string, '')
            line = line.replace("'", "")
            line = line.replace('"', '')
            return line

def main():
    common.check_filesystem()

    message.sub_info('Doing sanity checks')
    lsb_file = misc.join_paths(config.FILESYSTEM_DIR, 'etc/lsb-release')
    if not os.path.isfile(lsb_file):
        message.sub_critical(lsb_file + ' does not exists')
        sys.exit(2)

    isolinux_dir = misc.join_paths(config.ISO_DIR, 'isolinux')
    if not os.path.isdir(isolinux_dir):
        message.sub_critical(isolinux_dir + ' does not exist')
        sys.exit(2)

    casper_dir = misc.join_paths(config.ISO_DIR, 'casper')
    if not os.path.isdir(casper_dir):
        os.makedirs(casper_dir)

    base_file = misc.join_paths(config.ISO_DIR, '.disk/base_installable')
    if os.path.isfile(misc.join_paths(config.FILESYSTEM_DIR, 'usr/bin/ubiquity')):
        if not os.path.isfile(base_file):
            misc.write_file(base_file, '')
    elif os.path.isfile(base_file):
        os.unlink(base_file)

    message.sub_info('Gathering information')
    arch = misc.chroot_exec(('dpkg', '--print-architecture'), prepare=False, mount=False, output=True)
    distrib = search(config.FILESYSTEM_DIR + '/etc/lsb-release', 'DISTRIB_ID=')
    release = search(config.FILESYSTEM_DIR + '/etc/lsb-release', 'DISTRIB_RELEASE=')

    message.sub_info('Cleaning up')
    for sfile in ('casper/filesystem.squashfs', 'casper/initrd.lz', 'casper/vmlinuz',
        'casper/vmlinuz.efi', 'casper/filesystem.manifest', 'casper/filesystem.manifest-desktop'
        'casper/filesystem.size', 'md5sum.txt'):

        full_file = misc.join_paths(config.ISO_DIR, sfile)
        if os.path.exists(full_file):
            os.unlink(full_file)

    iso_file = '/home/%s-%s-%s.iso' % (distrib, arch, release)
    if os.path.exists(iso_file):
        os.unlink(iso_file)

    message.sub_info('Updating/creating Kernel images')
    misc.chroot_exec(('update-initramfs', '-k', 'all', '-t', '-u'))

    initrd = None
    vmlinuz = None
    for sfile in misc.list_files(misc.join_paths(config.FILESYSTEM_DIR, 'boot')):
        if 'initrd.img' in sfile:
            initrd = sfile
        elif 'vmlinuz' in sfile:
            vmlinuz = sfile

    if not initrd or not vmlinuz:
        message.sub_critical('Missing boot file (initrd or vmlinuz)')
        sys.exit(2)
    else:
        misc.copy_file(initrd, misc.join_paths(config.ISO_DIR, 'casper/initrd.lz'))
        misc.copy_file(vmlinuz, misc.join_paths(config.ISO_DIR, 'casper/vmlinuz'))
        if os.path.isdir(misc.join_paths(config.ISO_DIR, 'efi/boot')):
            misc.copy_file(vmlinuz, misc.join_paths(config.ISO_DIR, 'casper/vmlinuz.efi'))

    if config.BOOT_FILES:
        message.sub_info('Deleteing boot files')
        for sfile in misc.list_files(misc.join_paths(config.FILESYSTEM_DIR, 'boot')):
            os.unlink(initrd)
            os.unlink(vmlinuz)

    message.sub_info('Creating squashed FileSystem')
    subprocess.check_call(('mksquashfs', config.FILESYSTEM_DIR,
                misc.join_paths(config.ISO_DIR, 'casper/filesystem.squashfs'),
                '-wildcards', '-ef', '/usr/share/customizer/exclude.list', '-comp', config.COMPRESSION))

    message.sub_info('Checking filesystem size')
    fs_size = os.path.getsize(misc.join_paths(config.ISO_DIR, 'casper/filesystem.squashfs'))
    if fs_size > 4000000000:
        message.sub_critical('The squashed filesystem size is greater than 4GB')
        sys.exit(2)

    message.sub_info('Creating filesystem.size')
    misc.write_file(misc.join_paths(config.ISO_DIR, 'casper/filesystem.size'), str(fs_size))

    message.sub_info('Creating filesystem.manifest')
    packages_list = misc.chroot_exec(("dpkg-query", "-W", "--showformat=${Package} ${Version}\\n"), prepare=False, mount=False, output=True)
    misc.write_file(misc.join_paths(config.ISO_DIR, 'casper/filesystem.manifest'), packages_list)

    message.sub_info('Creating filesystem.manifest-desktop')
    for pkg in ('ubiquity', 'casper', 'live-initramfs', 'user-setup', 'discover1', 'xresprobe', 'libdebian-installer4'):
        packages_list.replace(pkg, '')
    misc.write_file(misc.join_paths(config.ISO_DIR, 'casper/filesystem.manifest-desktop'), packages_list)

    message.sub_info('Creating MD5Sums')
    checksum_file = misc.join_paths(config.ISO_DIR, 'md5sum.txt')
    misc.write_file(checksum_file, '')
    for sfile in misc.list_files(config.ISO_DIR):
        if sfile.endswith('md5sum.txt'):
            continue

        # FIXME: read in chunks
        checksum = hashlib.md5(misc.read_file(sfile)).hexdigest()
        misc.append_file(checksum_file, checksum + '  .' + sfile.replace(config.ISO_DIR, '') +'\n')

    message.sub_info('Creating ISO')
    os.chdir(config.ISO_DIR)
    subprocess.check_call(('xorriso', '-as', 'mkisofs', '-r', '-V', distrib + '-' + arch + '-' + release,
    '-b', 'isolinux/isolinux.bin', '-c', 'isolinux/boot.cat', '-cache-inodes',
    '-J', '-l', '-no-emul-boot', '-boot-load-size', '4', '-boot-info-table',
    '-o', iso_file, '-input-charset', 'utf-8', '.'))
    # chmod 555 "/home/$DIST-$ARCH-$VERSION.iso"

    message.sub_info('Successfuly created ISO image', iso_file)
