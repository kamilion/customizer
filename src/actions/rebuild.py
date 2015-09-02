#!/usr/bin/python2

import sys, os, glob, shutil, re, hashlib

import lib.misc as misc
import lib.config as config
import lib.message as message
import actions.common as common

def detect_boot():
    global initrd, vmlinuz, mt86plus, xen_kernel, xen_efi, ipxe_kernel, ipxe_efi
    initrd = None
    vmlinuz = None
    mt86plus = None
    xen_kernel = None
    xen_efi = None
    ipxe_kernel = None
    ipxe_efi = None

    for sfile in sorted(misc.list_files(misc.join_paths(config.FILESYSTEM_DIR, 'boot'))):
        if 'initrd.img' in sfile:
            initrd = sfile
            message.sub_debug('Initrd detected', sfile)
        elif 'vmlinuz' in sfile:
            vmlinuz = sfile
            message.sub_debug('Vmlinuz detected', sfile)
        elif 'memtest86' in sfile:
            if '+.bin' in sfile:
                # In theory, We want memtest86+.bin, not memtest86+_multiboot.bin
                # But in actual practice, they're often the same file. Let's be picky.
                mt86plus = sfile
                message.sub_debug('Memtest86+ kernel detected', sfile)
        elif 'xen' in sfile:
            if 'gz' in sfile:
                xen_kernel = sfile
                message.sub_debug('Xen Hypervisor kernel detected', sfile)
            if 'efi' in sfile:
                xen_efi = sfile
                message.sub_debug('Xen Hypervisor EFI kernel detected', sfile)
        elif 'ipxe' in sfile:
            if 'lkrn' in sfile:
                ipxe_kernel = sfile
                message.sub_debug('iPXE kernel detected', sfile)
            if 'efi' in sfile:
                ipxe_efi = sfile
                message.sub_debug('iPXE EFI kernel detected', sfile)

def main():
    common.check_filesystem()

    # Basic sanity checks of files and paths that absolutely need to exist.
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

    # Acquire distribution information from the FileSystem
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

    # Remove files, by name, that we know we must repopulate if they exist.
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

    # Define the checksum files, and the ISO filename.
    md5sum_iso_file = misc.join_paths(config.WORK_DIR, 'md5sum')
    sha1sum_iso_file = misc.join_paths(config.WORK_DIR, 'sha1sum')
    sha256sum_iso_file = misc.join_paths(config.WORK_DIR, 'sha256sum')
    iso_file = '%s/%s-%s-%s.iso' % (config.WORK_DIR, distrib, arch, release)
    if os.path.exists(iso_file):
        message.sub_debug('Removing', iso_file)
        os.unlink(iso_file)
    if os.path.exists(md5sum_iso_file):
        message.sub_debug('Removing', md5sum_iso_file)
        os.unlink(md5sum_iso_file)
    if os.path.exists(sha1sum_iso_file):
        message.sub_debug('Removing', sha1sum_iso_file)
        os.unlink(sha1sum_iso_file)
    if os.path.exists(sha256sum_iso_file):
        message.sub_debug('Removing', sha256sum_iso_file)
        os.unlink(sha256sum_iso_file)

    # Detect files needed for booting, the kernel, initramfs, xen and anything else.
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
            os.link(misc.join_paths(config.ISO_DIR, \
                'casper/vmlinuz.efi'), misc.join_paths(config.ISO_DIR, \
                'casper/vmlinuz'))
            # EFI Kernels are still loadable by grub, modern ISOs lack a bare vmlinuz.
            # mkisofs/genisoimage -cache-inodes reuses hard linked inodes.
        else:
            misc.copy_file(vmlinuz, misc.join_paths(config.ISO_DIR, 'casper/vmlinuz'))
            # We only need to copy the bare kernel if we're not using EFI at all.

        # Copy optional boot-enablement packages onto the ISO, if found.
        if mt86plus:
            message.sub_debug('Memtest86+ kernel', mt86plus)
            misc.copy_file(mt86plus, misc.join_paths(config.ISO_DIR, 'install/mt86plus'))
        if xen_kernel:
            message.sub_debug('Xen kernel', xen_kernel)
            misc.copy_file(xen_kernel, \
                misc.join_paths(config.ISO_DIR, 'casper/' + os.path.basename(xen_kernel)))
        if xen_efi:
            message.sub_debug('Xen EFI kernel', xen_efi)
            misc.copy_file(xen_efi, \
                misc.join_paths(config.ISO_DIR, 'casper/' + os.path.basename(xen_efi)))
        if ipxe_kernel:
            message.sub_debug('iPXE kernel', ipxe_kernel)
            misc.copy_file(ipxe_kernel, \
                misc.join_paths(config.ISO_DIR, 'casper/' + os.path.basename(ipxe_kernel)))
        if ipxe_efi:
            message.sub_debug('iPXE EFI kernel', ipxe_efi)
            misc.copy_file(ipxe_efi, \
                misc.join_paths(config.ISO_DIR, 'casper/' + os.path.basename(ipxe_efi)))

    message.sub_info('Extracting casper UUID')
    confdir = config.FILESYSTEM_DIR + '/conf'
    if os.path.isdir(confdir):
        shutil.rmtree(confdir)
    os.makedirs(confdir)
    try:
        misc.chroot_exec('zcat ' + initrd.replace(config.FILESYSTEM_DIR, '') + ' | cpio --quiet -id conf/uuid.conf', \
            shell=True, cwd=config.FILESYSTEM_DIR)
        kernel = re.search('initrd.img-*.*.*-*-(.*)', initrd).group(1)
        message.sub_debug('Kernel', kernel)
        misc.copy_file(confdir + '/uuid.conf', misc.join_paths(config.ISO_DIR, \
            '.disk/casper-uuid-' + kernel))
    finally:
        shutil.rmtree(confdir)

    # Define some default compression parameters, including a 1MB blocksize for all compressors.
    compression_parameters = ('-b', '1048576', '-comp', config.COMPRESSION)
    if config.COMPRESSION == 'xz':  # Append additional compression parameters for xz.
        # Using the branch-call-jump filter provides a compression boost with executable code.
        # This can save a hundred megabytes easily, on an 800MB ISO. The dictionary size must
        # match the block size, and it's advisable to use larger block sizes, like 1MB or 4MB.
        compression_parameters += ('-Xbcj', 'x86', '-Xdict-size', '100%')
    message.sub_info('SquashFS Compression parameters', compression_parameters)

    # Create the compressed filesystem
    message.sub_info('Creating SquashFS Compressed Filesystem')
    make_squash_fs = ('mksquashfs', config.FILESYSTEM_DIR, \
        misc.join_paths(config.ISO_DIR, 'casper/filesystem.squashfs'), \
        '-wildcards', '-no-recovery', '-noappend', \
        '-ef', os.path.join(sys.prefix, 'share/customizer/exclude.list'))
    misc.system_command(make_squash_fs + compression_parameters)

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

    # Creating a md5sum.txt file fixes lubuntu's integrity check.
    md5sums_file = misc.join_paths(config.ISO_DIR, 'md5sum.txt')
    if os.path.isfile(md5sums_file):
        message.sub_info('Creating md5sum.txt')
        misc.write_file(md5sums_file, '')
        for sfile in misc.list_files(config.ISO_DIR):
            if sfile.endswith('md5sum.txt'):
                continue
            if sfile.endswith('SHA256SUMS'):
                continue

            # FIXME: read in chunks
            message.sub_debug('MD5 Checksumming', sfile)
            checksum = hashlib.md5(misc.read_file(sfile)).hexdigest()
            misc.append_file(md5sums_file, checksum + '  .' + \
                sfile.replace(config.ISO_DIR, '') +'\n')

    # Creating a SHA256SUMS file fixes ubuntu-mini-remix's integrity check.
    shasums_file = misc.join_paths(config.ISO_DIR, 'SHA256SUMS')
    if os.path.isfile(shasums_file):
        message.sub_info('Creating SHA256SUMS')
        misc.write_file(shasums_file, '')
        for sfile in misc.list_files(config.ISO_DIR):
            if sfile.endswith('md5sum.txt'):
                continue
            if sfile.endswith('SHA256SUMS'):
                continue

            # FIXME: read in chunks
            message.sub_debug('SHA256 Checksumming', sfile)
            checksum = hashlib.sha256(misc.read_file(sfile)).hexdigest()
            misc.append_file(shasums_file, checksum + '  .' + \
                sfile.replace(config.ISO_DIR, '') +'\n')

    # Create the ISO filesystem
    message.sub_info('Creating ISO')
    os.chdir(config.ISO_DIR)
    misc.system_command(('xorriso', '-as', 'mkisofs', '-r', '-V', \
        distrib + '-' + arch + '-' + release, '-b', 'isolinux/isolinux.bin', \
        '-c', 'isolinux/boot.cat', '-J', '-l', '-no-emul-boot', \
        '-boot-load-size', '4', '-boot-info-table', '-o', iso_file, \
        '-cache-inodes', '-input-charset', 'utf-8', '.'))

    message.sub_info('Creating ISO checksums')
    md5checksum = hashlib.md5(misc.read_file(iso_file)).hexdigest()
    message.sub_info('ISO md5 checksum', md5checksum)
    misc.append_file(md5sum_iso_file, md5checksum + '  .' + \
        iso_file.replace(config.WORK_DIR, '') +'\n')
    sha1checksum = hashlib.sha1(misc.read_file(iso_file)).hexdigest()
    message.sub_info('ISO sha1 checksum', sha1checksum)
    misc.append_file(sha1sum_iso_file, sha1checksum + '  .' + \
        iso_file.replace(config.WORK_DIR, '') +'\n')
    sha256checksum = hashlib.sha256(misc.read_file(iso_file)).hexdigest()
    message.sub_info('ISO sha256 checksum', sha256checksum)
    misc.append_file(sha256sum_iso_file, sha256checksum + '  .' + \
        iso_file.replace(config.WORK_DIR, '') +'\n')

    message.sub_info('Successfuly created ISO image', iso_file)
