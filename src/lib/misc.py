#!/usr/bin/python2

import os, re, shutil, shlex, subprocess

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


''' File operations '''
def read_file(sfile):
    rfile = open(sfile, 'r')
    content = rfile.read()
    rfile.close()
    return content

def readlines_file(sfile):
    rfile = open(sfile, 'r')
    content = rfile.readlines()
    rfile.close()
    return content

def write_file(sfile, content):
    dirname = os.path.dirname(sfile)
    if not os.path.isdir(dirname):
        os.makedirs(dirname)

    wfile = open(sfile, 'w')
    wfile.write(content)
    wfile.close()

def append_file(sfile, content):
    dirname = os.path.dirname(sfile)
    if not os.path.isdir(dirname):
        os.makedirs(dirname)

    afile = open(sfile, 'a')
    afile.write(content)
    afile.close()

def copy_file(source, destination):
    base = os.path.dirname(destination)
    if not os.path.isdir(base):
        os.makedirs(base)
    shutil.copyfile(source, destination)

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
    return search_string(string, read_file(sfile), exact=exact, escape=escape)

def list_files(directory):
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

def system_command(command, shell=False, cwd=None, catch=False):
    if not cwd:
        cwd = dir_current()
    elif not os.path.isdir(cwd):
        cwd = '/'
    if isinstance(command, str) and not shell:
        command = shlex.split(command)
    if catch or CATCH:
        pipe = subprocess.Popen(command, stderr=subprocess.PIPE, \
            shell=shell, cwd=cwd)
        pipe.wait()
        if pipe.returncode != 0:
            raise(Exception(pipe.communicate()[1].strip()))
        return pipe.returncode
    else:
        return subprocess.check_call(command, shell=shell, cwd=cwd)

def chroot_exec(command, prepare=True, mount=True, output=False, xnest=False, shell=False):
    real_root = os.open('/', os.O_RDONLY)
    try:
        if prepare:
            if os.path.isfile('/etc/resolv.conf'):
                copy_file('/etc/resolv.conf', \
                    config.FILESYSTEM_DIR + '/etc/resolv.conf')
            if os.path.isfile('/etc/hosts'):
                copy_file('/etc/hosts', config.FILESYSTEM_DIR + '/etc/hosts')

        if mount:
            pseudofs = ['/proc', '/dev', '/sys', '/tmp', '/var/lib/dbus']
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
                    if s == '/dev':
                        system_command((whereis('mount'), '--rbind', s, sdir))
                    else:
                        system_command((whereis('mount'), '--bind', s, sdir))


        os.chroot(config.FILESYSTEM_DIR)
        os.chdir('/')
        if prepare:
            if not os.path.isfile('/etc/mtab'):
                os.symlink('/proc/mounts', '/etc/mtab')

        if not config.LOCALES == 'C':
            system_command(('locale-gen', config.LOCALES))

        os.putenv('PATH', '/usr/sbin:/usr/bin:/sbin:/bin')
        os.putenv('HOME', '/root')
        os.putenv('LC_ALL', config.LOCALES)
        os.putenv('LANGUAGE', config.LOCALES)
        os.putenv('LANG', config.LOCALES)
        os.putenv('CASPER_GENERATE_UUID', '1')
        if not xnest:
            os.putenv('DEBIAN_FRONTEND', 'noninteractive')
            # FIXME: os.putenv('DEBIAN_PRIORITY', '')
            os.putenv('DEBCONF_NONINTERACTIVE_SEEN', 'true')
            os.putenv('DEBCONF_NOWARNINGS', 'true')

        if xnest:
            os.putenv('HOME', '/etc/skel')
            os.putenv('XDG_CACHE_HOME', '/etc/skel/.cache')
            os.putenv('XDG_DATA_HOME', '/etc/skel/.local/share')
            os.putenv('XDG_CONFIG_HOME', '/etc/skel/.config')
            os.putenv('DISPLAY', ':13')

        if output:
            out = get_output(command)
        else:
            system_command(command, shell=shell)
    finally:
        os.fchdir(real_root)
        os.chroot('.')
        os.close(real_root)

        if mount:
            for s in reversed(pseudofs):
                sdir = config.FILESYSTEM_DIR + s
                if os.path.ismount(sdir):
                    system_command((whereis('umount'), '-f', '-l', sdir))
    if output:
        return out
