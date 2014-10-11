#!/usr/bin/python2

import sys, os, tempfile, subprocess

import lib.misc as misc
import lib.config as config
import lib.message as message
import actions.common as common

# TODO: this is not the best way to do it, exception can be raised at any time
mount_dir = None
def unmount_iso():
    if not mount_dir:
        return
    message.sub_info('Unmounting', mount_dir)
    misc.system_command((misc.whereis('umount'), '-f', mount_dir))

    message.sub_info('Removing', mount_dir)
    os.rmdir(mount_dir)

def main():
    global mount_dir
    if not os.path.isfile(config.ISO):
        message.sub_critical('ISO does not exists', config.ISO)
        sys.exit(2)
    elif not config.ISO.endswith('.iso'):
        message.sub_critical('File is not ISO', config.ISO)
        sys.exit(2)

    common.clean_work_dirs()
    common.create_work_dirs()

    message.sub_info('Creating mount directory')
    mount_dir = tempfile.mkdtemp(prefix=config.MOUNT_DIR + '/')
    message.sub_debug('Mount directory is', mount_dir)

    message.sub_info('Mounting ISO', config.ISO)
    try:
        misc.system_command((misc.whereis('mount'), '-t', 'iso9660', '-o', \
            'ro,loop', config.ISO, mount_dir))
    except:
        common.clean_work_dirs()
        raise

    message.sub_info('Checking ISO')
    for spath in (mount_dir + '/casper/filesystem.squashfs', \
        mount_dir + '/casper/filesystem.manifest',
        mount_dir + '/casper/filesystem.manifest-remove',
        mount_dir + '/.disk', mount_dir + '/isolinux', ):
        if not os.path.exists(spath):
            message.sub_debug('Non-existing path', spath)
            message.sub_critical('Invalid ISO', config.ISO)
            common.clean_work_dirs()
            unmount_iso()
            sys.exit(2)

    message.sub_info('Unsquashing filesystem')
    try:
        misc.system_command((misc.whereis('unsquashfs'), '-f', '-d', \
            config.FILESYSTEM_DIR, mount_dir + '/casper/filesystem.squashfs'))
    except:
        unmount_iso()
        raise

    message.sub_info('Checking architecture')
    fs_arch = misc.chroot_exec(('dpkg', '--print-architecture'), \
        prepare=False, mount=False, output=True)
    host_arch = os.uname()[4]
    message.sub_debug('Filesystem architecture', fs_arch)
    message.sub_debug('Host architecture', host_arch)
    if fs_arch == 'amd64' and not host_arch == 'x86_64':
        message.sub_critical('The ISO architecture is amd64 and yours is not')
        common.clean_work_dirs()
        unmount_iso()
        sys.exit(2)

    message.sub_info('Copying ISO files')
    for sfile in misc.list_files(mount_dir):
        if sfile.endswith('casper/filesystem.squashfs'):
            continue
        else:
            message.sub_debug('Copying', sfile)
            misc.copy_file(sfile, sfile.replace(mount_dir, config.ISO_DIR))

    unmount_iso()
