#!/usr/bin/python2.7

import os

import lib.misc as misc
import lib.config as config
import lib.message as message
import actions.common as common

def main():
    common.check_filesystem()

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

    if isinstance(arch, bytes):  # For some reason this is of type 'bytes'.
        if int(sys.version_info[0]) >= 3:  # If we're running under python3
            arch = str(arch, 'utf-8')
        else:  # Otherwise just cast it to a str without the 'utf-8' option.
            arch = str(arch)
    
    iso_file = '%s/%s-%s-%s.iso' % (config.WORK_DIR, distrib, arch, release)
    if not os.path.exists(iso_file):
        raise(message.exception('ISO image does not exist', iso_file))

    message.sub_info('Running QEMU with ISO image', iso_file)
    host_arch = os.uname()[4]
    if host_arch == 'x86_64':
        qemu = misc.whereis('qemu-system-x86_64')
    else:
        qemu = misc.whereis('qemu-system-i386')
    if not qemu:
        raise(message.exception('QEMU is not installed'))

    qemu_kvm = False
    command = [qemu, '-m', config.VRAM, '-cdrom', iso_file]
    if misc.search_string('-enable-kvm', misc.get_output((qemu, '-h'))):
        qemu_kvm = True
    # CPU flag: "vmx" for Intel processors, "svm" for AMD processors
    # These flags are hidden in Xen environment
    # https://wiki.xenproject.org/wiki/Xen_Common_Problems
    host_kvm = False
    if os.path.exists('/dev/kvm') and os.path.exists('/proc/cpuinfo') and \
        misc.search_file('(?:\\s|^)flags.*(?:\\s)(vmx|svm)(?:\\s|$)', \
        '/proc/cpuinfo', escape=False):
        host_kvm = True
    if qemu_kvm and host_kvm:
        command.append('-enable-kvm')
    message.sub_debug('Host architecture', host_arch)
    message.sub_debug('QEMU KVM', qemu_kvm)
    message.sub_debug('Host KVM', host_kvm)
    misc.system_command(command)
