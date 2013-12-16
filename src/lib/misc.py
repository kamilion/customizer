#!/usr/bin/python2

import os, re, shutil, subprocess

import lib.config as config

def whereis(program, chroot=False):
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
    for root, subdirs, files in os.walk(directory):
        for sfile in files:
            slist.append(os.path.join(root, sfile))
    return slist

def chroot_exec(command, prepare=True, mount=True, output=False, xnest=False):
    pseudofs = ['/proc', '/dev', '/sys']
    if xnest:
        if os.path.islink(config.FILESYSTEM_DIR + '/var/run'):
            pseudofs.append('/run/dbus')
        else:
            pseudofs.append('/var/run/dbus')
        pseudofs.append('/var/lib/dbus')

    real_root = os.open('/', os.O_RDONLY)
    try:
        if prepare:
            if os.path.isfile('/etc/resolv.conf'):
                copy_file('/etc/resolv.conf', config.FILESYSTEM_DIR + '/etc/resolv.conf')
            if os.path.isfile('/etc/hosts'):
                copy_file('/etc/hosts', config.FILESYSTEM_DIR + '/etc/hosts')

        if mount:
            for s in pseudofs:
                sdir = config.FILESYSTEM_DIR + s
                if not os.path.ismount(sdir):
                    if not os.path.isdir(sdir):
                        os.makedirs(sdir)
                    subprocess.check_call([whereis('mount'), '--rbind', s, sdir])

        os.chroot(config.FILESYSTEM_DIR)
        os.chdir('/')
        if prepare:
            if not os.path.isfile('/etc/mtab'):
                os.symlink('/proc/mounts', '/etc/mtab')

        os.putenv('HOME', '/root')
        os.putenv('LC_ALL', config.LOCALES)
        os.putenv('LANGUAGE', config.LOCALES)
        os.putenv('LANG', config.LOCALES)

        if xnest:
            os.putenv('HOME', '/etc/skel')
            os.putenv('XDG_CACHE_HOME', '/etc/skel/.cache')
            os.putenv('XDG_DATA_HOME', '/etc/skel')
            os.putenv('XDG_CONFIG_HOME', '/etc/skel/.config')
            os.putenv('DISPLAY', ':9')

        if output:
            out = get_output(command)
        else:
            subprocess.check_call(command)
    finally:
        os.fchdir(real_root)
        os.chroot(".")
        os.close(real_root)

        if mount:
            for s in reversed(pseudofs):
                sdir = config.FILESYSTEM_DIR + s
                if os.path.ismount(sdir):
                    subprocess.check_call((whereis('umount'), '--force', '--lazy', sdir))
        if output:
            return out
