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
    subprocess.check_call((misc.whereis('umount'), '-f', mount_dir))

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

    message.sub_info('Creating mount dir')
    mount_dir = tempfile.mkdtemp(prefix=config.MOUNT_DIR + '/')

    message.sub_info('Mounting ISO', config.ISO)
    subprocess.check_call((misc.whereis('mount'), '-t', 'iso9660', '-o', 'ro,loop', config.ISO, mount_dir))

    message.sub_info('Checking ISO')
    for sfile in (mount_dir + '/casper/filesystem.squashfs', mount_dir + '/.disk', mount_dir + '/isolinux'):
        if not os.path.exists(sfile):
            message.sub_critical('Invalid ISO', config.ISO)
            common.clean_work_dirs()
            unmount_iso()
            sys.exit(2)

    message.sub_info('Unsquashing filesystem')
    try:
        subprocess.check_call((misc.whereis('unsquashfs'), '-f', '-d', config.FILESYSTEM_DIR, mount_dir + '/casper/filesystem.squashfs'))
    except:
        unmount_iso()
        raise

    message.sub_info('Checking architecture')
    architecture = misc.chroot_exec(('dpkg', '--print-architecture'), prepare=False, mount=False, output=True)
    if architecture == 'amd64' and not os.uname()[4] == 'x86_64':
        message.sub_critical('The ISO architecture is amd64 and yours is not')
        common.clean_work_dirs()
        unmount_iso()
        sys.exit(2)

    message.sub_info('Copying ISO files')
    for sfile in misc.list_files(mount_dir):
        if sfile.startswith(mount_dir + '/casper'):
            continue
        elif sfile == mount_dir + '/md5sum.txt':
            continue
        else:
            misc.copy_file(sfile, sfile.replace(mount_dir, config.ISO_DIR))

    unmount_iso()
