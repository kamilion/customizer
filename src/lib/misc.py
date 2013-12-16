#!/usr/bin/python2

import os, re, shutil, subprocess

import lib.config as config

def check_uid():
    if os.geteuid() == 0:
        return True
    return False

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


''' Directory operations '''
def remove_dir(sdir):
    for root, dirs, files in os.walk(sdir):
        for f in files:
            os.unlink(root + '/'  + f)
        for d in dirs:
            if os.path.islink(root + '/'  + d):
                os.unlink(root + '/'  + d)
    for root, dirs, files in os.walk(sdir, topdown=False):
        for d in dirs:
            os.rmdir(root + '/'  + d)
    os.rmdir(sdir)

def copy_dir(src, dst, symlinks=True, ignore=None):
    if not os.path.exists(dst):
        os.makedirs(dst)
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, symlinks, ignore)
        else:
            if not os.path.exists(d) or os.stat(src).st_mtime - os.stat(dst).st_mtime > 1:
                shutil.copy2(s, d)

def move_dir(src, dst):
    for src_dir, dirs, files in os.walk(src, topdown=True, onerror=None, followlinks=False):
        dst_dir = src_dir.replace(src, dst)
        if not os.path.exists(dst_dir):
            os.makedirs(dst_dir)
        for file_ in files:
            src_file = os.path.join(src_dir, file_)
            dst_file = os.path.join(dst_dir, file_)
            if os.path.exists(dst_file):
                os.remove(dst_file)
            shutil.move(src_file, dst_dir)

def size_dir(src):
    total_size = 0
    for sfile in list_files(src):
        if os.path.islink(sfile):
            continue

        total_size += os.path.getsize(sfile)
    return total_size


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

def list_dirs(directory):
    slist = []
    for root, subdirs, files in os.walk(directory):
        for sdir in subdirs:
            slist.append(os.path.join(root, sdir))
    return slist

def chroot_exec(command, prepare=True, mount=True, output=False, xnest=False):
    pseudofs = ['/proc', '/dev', '/sys']
    if xnest:
        pseudofs.extend(('/var/lib/dbus', '/var/run/dbus'))

    real_root = os.open('/', os.O_RDONLY)
    try:
        # FIXME: /proc/mtab
        if prepare:
            if os.path.isfile('/etc/resolv.conf'):
                copy_file('/etc/resolv.conf', config.FILESYSTEM_DIR + '/etc/resolv.conf')

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

        if xnest:
            os.putenv('DISPLAY', ':9')

        if output:
            output = get_output(command)
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
        return output
