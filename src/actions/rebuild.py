#!/usr/bin/python2

import sys, os, glob, shutil, re, hashlib

import lib.misc as misc
import lib.config as config
import lib.message as message
import actions.common as common

def detect_boot():
    global initrd, vmlinuz
    initrd = None
    vmlinuz = None

    for sfile in sorted(misc.list_files(misc.join_paths(config.FILESYSTEM_DIR, 'boot'))):
        if 'initrd.img' in sfile:
            initrd = sfile
            message.sub_debug('Initrd detected', sfile)
        elif 'vmlinuz' in sfile:
            vmlinuz = sfile
            message.sub_debug('Vmlinuz detected', sfile)


def main():
    common.check_filesystem()

    message.sub_info('Doing sanity checks')
    lsb_file = misc.join_paths(config.FILESYSTEM_DIR, 'etc/lsb-release')
    if not os.path.isfile(lsb_file):
        raise(message.exception(lsb_file + ' does not exists'))

    isolinux_dir = misc.join_paths(config.ISO_DIR, 'isolinux')
    if not os.path.isdir(isolinux_dir):
        raise(message.exception(isolinux_dir + ' does not exist'))

    if misc.search_file('999:999', misc.join_paths(config.FILESYSTEM_DIR, 'etc/passwd')):
        raise(message.exception('User with UID 999 exists, this mean that automatic login will fail'))
    elif misc.search_file('999:999', misc.join_paths(config.FILESYSTEM_DIR, 'etc/group')):
        raise(message.exception('Group with GID 999 exists, this mean that automatic login will fail'))

    casper_dir = misc.join_paths(config.ISO_DIR, 'casper')
    if not os.path.isdir(casper_dir):
        message.sub_debug('Creating', casper_dir)
        os.makedirs(casper_dir)

    base_file = misc.join_paths(config.ISO_DIR, '.disk/base_installable')
    if os.path.isfile(misc.join_paths(config.FILESYSTEM_DIR, 'usr/bin/ubiquity')):
        if not os.path.isfile(base_file):
            message.sub_debug('Creating', base_file)
            misc.write_file(base_file, '')
    elif os.path.isfile(base_file):
        message.sub_debug('Removing', base_file)
        os.unlink(base_file)

    message.sub_info('Gathering information')
    arch = misc.chroot_exec(('dpkg', '--print-architecture'), prepare=False, \
        mount=False, output=True)
    distrib = common.get_value(config.FILESYSTEM_DIR + '/etc/lsb-release', \
        'DISTRIB_ID=')
    release = common.get_value(config.FILESYSTEM_DIR + '/etc/lsb-release', \
        'DISTRIB_RELEASE=')
    message.sub_debug('Architecture', arch)
    message.sub_debug('Distribution (DISTRIB_ID)', distrib)
    message.sub_debug('Release (DISTRIB_RELEASE)', release)

    message.sub_info('Cleaning up')
    cleanup_files = ['casper/filesystem.squashfs', 'casper/initrd.lz', \
        'casper/vmlinuz', 'casper/vmlinuz.efi', 'casper/filesystem.manifest', \
        'casper/filesystem.size']
    cleanup_files.extend(glob.glob('.disk/casper-uuid-*'))
    for sfile in cleanup_files:
        full_file = misc.join_paths(config.ISO_DIR, sfile)
        if os.path.exists(full_file):
            message.sub_debug('Removing', full_file)
            os.unlink(full_file)

    iso_file = '%s/%s-%s-%s.iso' % (config.WORK_DIR, distrib, arch, release)
    if os.path.exists(iso_file):
        message.sub_debug('Removing', iso_file)
        os.unlink(iso_file)

    detect_boot()
    if not vmlinuz:
        message.sub_info('Re-installing kernel')
        misc.chroot_exec(('apt-get', 'purge', '--yes', 'linux-image*', '-q'))
        misc.chroot_exec(('apt-get', 'install', '--yes', \
            'linux-image-generic', '-q'))
        misc.chroot_exec(('apt-get', 'clean'))
    else:
        message.sub_info('Updating initramfs')
        misc.chroot_exec(('update-initramfs', '-k', 'all', '-t', '-u'))
    detect_boot()

    if not initrd or not vmlinuz:
        raise(message.exception('Missing boot file (initrd or vmlinuz)'))
    else:
        message.sub_info('Copying boot files')
        message.sub_debug('Initrd', initrd)
        message.sub_debug('Vmlinuz', vmlinuz)
        misc.copy_file(initrd, misc.join_paths(config.ISO_DIR, 'casper/initrd.lz'))
        misc.copy_file(vmlinuz, misc.join_paths(config.ISO_DIR, 'casper/vmlinuz'))
        # FIXME: extend to support grub
        efi_boot_entry = False
        isolinux_dir = config.ISO_DIR + '/isolinux'
        if os.path.isdir(isolinux_dir):
            for sfile in os.listdir(isolinux_dir):
                if sfile.endswith('.cfg') and misc.search_file('vmlinuz.efi', isolinux_dir + '/' + sfile):
                    message.sub_debug('Found EFI entry in isolinux conf', sfile)
                    efi_boot_entry = True
        if os.path.isdir(misc.join_paths(config.ISO_DIR, 'efi/boot')) or \
            efi_boot_entry:
            message.sub_debug('Copying EFI vmlinuz')
            misc.copy_file(vmlinuz, misc.join_paths(config.ISO_DIR, \
                'casper/vmlinuz.efi'))

    message.sub_info('Extracting casper UUID')
    confdir = config.FILESYSTEM_DIR + '/conf'
    if os.path.isdir(confdir):
        shutil.rmtree(confdir)
    os.makedirs(confdir)
    try:
        misc.chroot_exec('zcat ' + initrd.lstrip(config.FILESYSTEM_DIR) + ' | ' + ' cpio --quiet -id conf/uuid.conf', \
            shell=True, cwd=config.FILESYSTEM_DIR)
        kernel = re.search('initrd.img-*.*.*-*-(.*)', initrd).group(1)
        message.sub_debug('Kernel', kernel)
        misc.copy_file(confdir + '/uuid.conf', misc.join_paths(config.ISO_DIR, \
            '.disk/casper-uuid-' + kernel))
    finally:
        shutil.rmtree(confdir)

    message.sub_info('Creating squashed FileSystem')
    misc.system_command(('mksquashfs', config.FILESYSTEM_DIR, \
        misc.join_paths(config.ISO_DIR, 'casper/filesystem.squashfs'), \
        '-wildcards', '-ef', os.path.join(sys.prefix, 'share/customizer/exclude.list'), \
        '-comp', config.COMPRESSION))

    message.sub_info('Checking SquashFS filesystem size')
    sfs_size = os.path.getsize(misc.join_paths(config.ISO_DIR, \
        'casper/filesystem.squashfs'))
    message.sub_debug('SquashFS filesystem size', sfs_size)
    if sfs_size > 4000000000:
        raise(message.exception('The SquashFS filesystem size is greater than 4GB'))

    message.sub_info('Creating filesystem.size')
    fs_size = 0
    for root, subdirs, files in os.walk(config.FILESYSTEM_DIR):
        for sfile in files:
            sfull = os.path.join(root, sfile)
            if os.path.islink(sfull):
                continue
            # FIXME: respect ignored files from exclude.list
            fs_size += os.path.getsize(sfull)
    message.sub_debug('Root filesystem size', fs_size)
    misc.write_file(misc.join_paths(config.ISO_DIR, \
        'casper/filesystem.size'), str(fs_size))

    message.sub_info('Creating filesystem.manifest')
    lpackages = misc.chroot_exec(('dpkg-query', '-W', \
        '--showformat=${Package} ${Version}\\n'), prepare=False, mount=False, \
        output=True)
    message.sub_debug('Packages', lpackages)
    misc.write_file(misc.join_paths(config.ISO_DIR, \
        'casper/filesystem.manifest'), lpackages)

    # FIXME: do some kung-fu to check if packages are installed
    # and remove them from filesystem.manifest-remove if they are not

    md5sums_file = misc.join_paths(config.ISO_DIR, 'md5sum.txt')
    if os.path.isfile(md5sums_file):
        message.sub_info('Creating md5sum.txt')
        misc.write_file(md5sums_file, '')
        for sfile in misc.list_files(config.ISO_DIR):
            if sfile.endswith('md5sum.txt'):
                continue

            # FIXME: read in chunks
            message.sub_debug('Checksuming', sfile)
            checksum = hashlib.md5(misc.read_file(sfile)).hexdigest()
            misc.append_file(md5sums_file, checksum + '  .' + \
                sfile.replace(config.ISO_DIR, '') +'\n')

    message.sub_info('Creating ISO')
    os.chdir(config.ISO_DIR)
    misc.system_command(('xorriso', '-as', 'mkisofs', '-r', '-V', \
        distrib + '-' + arch + '-' + release, '-b', 'isolinux/isolinux.bin', \
        '-c', 'isolinux/boot.cat', '-J', '-l', '-no-emul-boot', \
        '-boot-load-size', '4', '-boot-info-table', '-o', iso_file, \
        '-input-charset', 'utf-8', '.'))

    message.sub_info('Successfuly created ISO image', iso_file)
