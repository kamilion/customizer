#!/usr/bin/python2

import os, re, shutil, shlex, subprocess, time

import lib.message as message
CMD_DEBUG = True
COPY_DEBUG = True
CHROOT_DEBUG = True
FILE_DEBUG = True
MOUNT_DEBUG = True

import lib.config as config
CATCH = False

def whereis(program, chroot=False):
    program = os.path.basename(program)
    for path in os.environ.get('PATH', '/bin:/usr/bin').split(':'):
        if chroot:
            exe = join_paths(config.FILESYSTEM_DIR, path, program)
        else:
            exe = join_paths(path, program)
        if os.path.isfile(exe):
            return exe
    return None


''' Variables operations '''
def strip_list(string):
    for char in ['[', ']', "'", ',']:
        string = str(string).replace(char, '')
    return string

def join_paths(*paths):
    result = '/'
    for p in paths:
        result = os.path.join(result, p.lstrip('/'))
    return os.path.normpath(result)

def join_work_path(*paths):
    return join_paths(config.WORK_DIR, paths)

def join_iso_path(*paths):
    return join_paths(config.ISO_DIR, paths)

def join_fs_path(*paths):
    return join_paths(config.FILESYSTEM_DIR, paths)


''' File operations '''
def read_file(sfile):
    if FILE_DEBUG: message.sub_debug('Reading entire file', sfile)
    rfile = open(sfile, 'r')
    content = rfile.read()
    rfile.close()
    return content

def readlines_file(sfile):
    if FILE_DEBUG: message.sub_debug('Reading lines from', sfile)
    rfile = open(sfile, 'r')
    content = rfile.readlines()
    rfile.close()
    return content

def write_file(sfile, content):
    if FILE_DEBUG: message.sub_debug('Writing data to', sfile)
    dirname = os.path.dirname(sfile)
    if not os.path.isdir(dirname):
        os.makedirs(dirname)

    original = None
    if os.path.isfile(sfile):
        original = read_file(sfile)
    wfile = open(sfile, 'w')
    try:
        wfile.write(content)
    except:
        if original:
            wfile.write(original)
        raise
    finally:
        wfile.close()

def append_file(sfile, content):
    if FILE_DEBUG: message.sub_debug('Appending data to', sfile)
    dirname = os.path.dirname(sfile)
    if not os.path.isdir(dirname):
        os.makedirs(dirname)

    afile = open(sfile, 'a')
    afile.write(content)
    afile.close()

def copy_file(source, destination):
    if COPY_DEBUG: message.sub_debug('File {} copied to'.format(source), destination)
    base = os.path.dirname(destination)
    if not os.path.isdir(base):
        os.makedirs(base)
    shutil.copyfile(source, destination)

def generate_hash_for_file(hashtype, filename, blocksize=2**20):
    m = hashlib.new(hashtype)
    with open(filename, "rb") as f:
        while True:
            buf = f.read(blocksize)
            if not buf:
                break
            m.update(buf)
    return m.hexdigest()

''' System operations '''
def get_output(command):
    pipe = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return pipe.communicate()[0].strip()

''' Misc '''
def search_string(string, string2, exact=False, escape=True):
    if exact and escape:
        return re.findall('(\\s|^)' + re.escape(string) + '(\\s|$)', strip_list(string2))
    elif exact:
        return re.findall('(\\s|^)' + string + '(\\s|$)', strip_list(string2))
    elif escape:
        return re.findall(re.escape(string), strip_list(string2))
    else:
        return re.findall(string, str(string2))

def search_file(string, sfile, exact=False, escape=True):
    if CMD_DEBUG: message.sub_debug('Searching {} for'.format(sfile), string)
    return search_string(string, read_file(sfile), exact=exact, escape=escape)

def list_files(directory):
    if CMD_DEBUG: message.sub_debug('Listing files in', directory)
    slist = []
    if not os.path.exists(directory):
        return slist
    for root, subdirs, files in os.walk(directory):
        for sfile in files:
            slist.append(os.path.join(root, sfile))
    return slist

def dir_current():
    try:
        cwd = os.getcwd()
    except OSError:
        cwd = '/'
    return cwd

def system_command(command, shell=False, cwd=None, env=None):
    message.sub_debug('Executing system command', command)
    if not cwd:
        cwd = dir_current()
    elif not os.path.isdir(cwd):
        cwd = '/'
    if not env:
        env = os.environ
    if isinstance(command, str) and not shell:
        command = shlex.split(command)
    if CATCH:
        pipe = subprocess.Popen(command, stderr=subprocess.PIPE, \
            shell=shell, cwd=cwd, env=env)
        pipe.wait()
        if pipe.returncode != 0:
            raise(Exception(pipe.communicate()[1].strip()))
        return pipe.returncode
    else:
        return subprocess.check_call(command, shell=shell, cwd=cwd, env=env)

def chroot_exec(command, prepare=True, mount=True, output=False, xnest=False, shell=False, cwd=None):
    if CHROOT_DEBUG: message.sub_debug('Trying to set up chroot command', command)
    out = None
    resolv = '{}/etc/resolv.conf'.format(config.FILESYSTEM_DIR)
    hosts = '{}/etc/hosts'.format(config.FILESYSTEM_DIR)
    mount = whereis('mount')
    umount = whereis('umount')
    chroot = whereis('chroot')
    if isinstance(command, str):
        chroot_command = '{} {} {}'.format(chroot, config.FILESYSTEM_DIR, command)
    else:
        chroot_command = [chroot, config.FILESYSTEM_DIR]
        chroot_command.extend(command)
    try:
        if prepare:
            if CHROOT_DEBUG: message.sub_debug('Preparing chroot environment for networking')
            if os.path.isfile('/etc/resolv.conf') and not os.path.islink(resolv):
                 copy_file('/etc/resolv.conf', resolv)
            elif os.path.islink(resolv):
                # usually /run/resolvconf/resolv.conf
                resolv = os.path.realpath(resolv)
                rdir = os.path.dirname(resolv)
                if not os.path.isdir(rdir):
                    os.makedirs(rdir)
                copy_file('/etc/resolv.conf', resolv)
            if os.path.isfile('/etc/hosts'):
                if os.path.isfile(hosts):
                    copy_file(hosts, '{}.backup'.format(hosts))
                copy_file('/etc/hosts', hosts)

        if mount:
            if CHROOT_DEBUG: message.sub_debug('Mounting paths inside chroot')
            pseudofs = ['/proc', '/dev', '/dev/pts', '/dev/shm', '/sys', '/tmp', '/var/lib/dbus']
            if os.path.islink(config.FILESYSTEM_DIR + '/var/run'):
                pseudofs.append('/run/dbus')
            else:
                pseudofs.append('/var/run/dbus')
            for s in pseudofs:
                if not os.path.exists(s):
                    continue
                sdir = config.FILESYSTEM_DIR + s
                if not os.path.ismount(sdir):
                    if not os.path.isdir(sdir):
                        os.makedirs(sdir)
                    if MOUNT_DEBUG: message.sub_debug('Mounting --bind {}'.format(s), sdir)
                    system_command((mount, '--bind', s, sdir))


        if prepare:
            if MOUNT_DEBUG: message.sub_debug('Creating mtab inside chroot')
            mtab = '{}/etc/mtab'.format(config.FILESYSTEM_DIR)
            if not os.path.isfile(mtab) and not os.path.islink(mtab):
                os.symlink('../../proc/mounts', mtab)

        if not config.LOCALES == 'C':
            system_command(('locale-gen', config.LOCALES))

        if CHROOT_DEBUG: message.sub_debug('Enumerating environment variables')
        # all operations on reference to os.environ change the environment!
        environment = {}
        for item in os.environ:
            # skip desktop environment specifiec variables because if a DE is
            # run in the chroot it may encounter some issues, e.g. with the
            # XDG menus
            if item.startswith('KDE_') or item == 'XDG_CURRENT_DESKTOP':
                continue
            environment[item] = os.environ.get(item)
        environment['PATH'] = '/usr/sbin:/usr/bin:/sbin:/bin'
        environment['HOME'] = '/root'
        environment['LC_ALL'] = config.LOCALES
        environment['LANGUAGE'] = config.LOCALES
        environment['LANG'] = config.LOCALES
        environment['USER'] = 'root'
        environment['CASPER_GENERATE_UUID'] = '1'
        if xnest:
            environment['HOME'] = '/etc/skel'
            environment['XDG_CACHE_HOME'] = '/etc/skel/.cache'
            environment['XDG_DATA_HOME'] = '/etc/skel/.local/share'
            environment['XDG_CONFIG_HOME'] = '/etc/skel/.config'
            environment['DISPLAY'] = ':13'
        else:
            environment['DEBIAN_FRONTEND'] = 'noninteractive'
            # FIXME: is this needed?
            # environment['DEBIAN_PRIORITY'] = ''
            environment['DEBCONF_NONINTERACTIVE_SEEN'] = 'true'
            environment['DEBCONF_NOWARNINGS'] = 'true'

        if output:
            if CHROOT_DEBUG: message.sub_debug('Entering chroot')
            out = get_output(chroot_command)
            if CHROOT_DEBUG: message.sub_debug('Exiting chroot')
        else:
            if CHROOT_DEBUG: message.sub_debug('Entering chroot')
            system_command(chroot_command, shell=shell, \
                env=environment, cwd=cwd)
            if CHROOT_DEBUG: message.sub_debug('Exiting chroot')
    finally:
        if prepare:
            if os.path.isfile('{}.backup'.format(hosts)):
                copy_file('{}.backup'.format(hosts), hosts)
                os.unlink('{}.backup'.format(hosts))
        if mount:
            for s in reversed(pseudofs):
                sdir = config.FILESYSTEM_DIR + s
                if os.path.ismount(sdir):
                    if MOUNT_DEBUG: message.sub_debug('Unmounting -f -l', sdir)
                    system_command((umount, '-f', '-l', sdir))
            time.sleep(0.1)  # Wait for lazy unmounts to unlazy...
        system_command(('sleep', '1')) # Make sure of it. (and log it)
    if output:
        return out
