#!/usr/bin/python2

import os, re, shutil, urllib2, tarfile, gzip, subprocess, traceback

import lib.message as message
import lib.configparser as configparser

def check_uid():
	message.sub_traceback(traceback.extract_stack(limit=2)[0])
	if os.geteuid() == 0:
		return True
	return False

def whereis(program, chroot=False):
    message.sub_traceback(traceback.extract_stack(limit=2)[0])
    for path in os.environ.get('PATH', '').split(':'):
        if chroot:
		exe = join_paths(configparser.FILESYSTEM_DIR, path, program)
	else:
		exe = join_paths(path, program)
	if os.path.isfile(exe):
            return exe
    return None

def check_connectivity():
    try:
        urllib2.urlopen('http://www.google.com', timeout=1)
        return True
    except urllib2.URLError:
        return False

def unique(string):
	new = []
	for s in string:
		if not search_string(s, new, exact=True):
			new.append(s)
	return new

''' Variables operations '''
def strip_list(string):
    message.sub_traceback(traceback.extract_stack(limit=2)[0])
    for char in ['[', ']', "'", ',']:
        string = str(string).replace(char, '')
    return string

def join_paths(*paths):
	message.sub_traceback(traceback.extract_stack(limit=2)[0])
	result = '/'
	for p in paths:
		result = os.path.join(result, p.lstrip('/'))
	return os.path.normpath(result)


''' Directory operations '''
def remove_dir(sdir):
	message.sub_traceback(traceback.extract_stack(limit=2)[0])
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
    message.sub_traceback(traceback.extract_stack(limit=2)[0])
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
	message.sub_traceback(traceback.extract_stack(limit=2)[0])
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
	message.sub_traceback(traceback.extract_stack(limit=2)[0])
	total_size = 0
	for sfile in list_files(src):
		if os.path.islink(sfile):
			continue
			
		total_size += os.path.getsize(sfile)
	return total_size

def fetch_check(url, destination):
	# not all requests can get content-lenght , this means that there is no way
	# to tell if the archive is corrupted (checking if size == 0 is not enough)
	# so the source is re-feteched   

	message.sub_traceback(traceback.extract_stack(limit=2)[0])
	remote_file = urllib2.urlopen(url)

	if os.path.isfile(destination):
		local_size = os.path.getsize(destination)
		remote_size = remote_file.headers.get("content-length")
				
		if not remote_size:
			return False
		elif int(local_size) == int(remote_size):
			return True
	else:
		return False

def fetch(url, destination):
	message.sub_traceback(traceback.extract_stack(limit=2)[0])
	remote_file = urllib2.urlopen(url)
	dest_dir = os.path.dirname(destination)
	
	if not os.path.isdir(dest_dir):
		os.makedirs(dest_dir)
	
	output = open(destination,'wb')
	output.write(remote_file.read())
	output.close()

''' Archive operations '''
def size_archive(star, sfile):
	message.sub_traceback(traceback.extract_stack(limit=2)[0])
	size = None
	tar = tarfile.open(star, 'r')
	for i in tar.getmembers():
		if i.name == sfile:
			size = i.size
	tar.close()
	return size

def compress_dir(src, dst, method='bz2'):
	message.sub_traceback(traceback.extract_stack(limit=2)[0])
	dirname = os.path.dirname(dst)
	if not os.path.isdir(dirname):
		os.makedirs(dirname)
		
	os.chdir(src)
	tar = tarfile.open(dst, 'w:' + method)
	tar.add(src, '/')
	tar.close()

def compress_file(sfile, dst, method='gz', enc='UTF-8'):
	message.sub_traceback(traceback.extract_stack(limit=2)[0])
	dirname = os.path.dirname(dst)
	if not os.path.isdir(dirname):
		os.makedirs(dirname)
		
	tar = tarfile.open(dst, 'w:' + method, encoding=enc)
	tar.add(sfile, '/')
	tar.close()

def gzip_file(sfile, dst):
	message.sub_traceback(traceback.extract_stack(limit=2)[0])
	dirname = os.path.dirname(dst)
	if not os.path.isdir(dirname):
		os.makedirs(dirname)
		
	f_in = open(sfile, 'rb')
	f_out = gzip.open(sfile + '.gz', 'wb')
	f_out.writelines(f_in)
	f_out.close()
	f_in.close()

def decompress_archive(src, dst):
	message.sub_traceback(traceback.extract_stack(limit=2)[0])
	if not os.path.isdir(dst):
		os.makedirs(dst)

	# FIXME: this is a workaround for xz archives
	if src.endswith('.xz'):
		subprocess.check_call([whereis('tar'), '-xaf', src, '-C', dst])
	else:
		tar = tarfile.open(src, 'r')
		os.chdir(dst)
		tar.extractall()
		tar.close()

def list_archive(src):
	message.sub_traceback(traceback.extract_stack(limit=2)[0])
	tar = tarfile.open(src)
	content = tar.getnames()
	tar.close()
	return content


''' File operations '''
def mime_file(sfile):
	message.sub_traceback(traceback.extract_stack(limit=2)[0])
	# return mimetypes.guess_type(file)
	return get_output([whereis('file'), '--brief', '--mime-type', sfile])

def read_file(sfile):
	message.sub_traceback(traceback.extract_stack(limit=2)[0])
	rfile = open(sfile, 'r')
	content = rfile.read()
	rfile.close()
	return content
	
def readlines_file(sfile):
	message.sub_traceback(traceback.extract_stack(limit=2)[0])
	rfile = open(sfile, 'r')
	content = rfile.readlines()
	rfile.close()
	return content
	
def write_file(sfile, content):
	message.sub_traceback(traceback.extract_stack(limit=2)[0])
	dirname = os.path.dirname(sfile)
	if not os.path.isdir(dirname):
		os.makedirs(dirname)

	wfile = open(sfile, 'w')
	wfile.write(content)
	wfile.close()

def append_file(sfile, content):
	message.sub_traceback(traceback.extract_stack(limit=2)[0])
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
	message.sub_traceback(traceback.extract_stack(limit=2)[0])
	pipe = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	return pipe.communicate()[0].strip()

''' Misc '''
def search_string(string, string2, exact=False, escape=True):
	message.sub_traceback(traceback.extract_stack(limit=2)[0])

	if exact and escape:
		return re.findall('(\\s|^)' + re.escape(string) + '(\\s|$)', strip_list(string2))
	elif exact:
		return re.findall('(\\s|^)' + string + '(\\s|$)', strip_list(string2))
	elif escape:
		return re.findall(re.escape(string), strip_list(string2))
	else:
		return re.findall(string, str(string2))

def search_file(string, sfile, exact=False, escape=True):
	message.sub_traceback(traceback.extract_stack(limit=2)[0])
	return search_string(string, read_file(sfile), exact=exact, escape=escape)

def list_files(directory):
	message.sub_traceback(traceback.extract_stack(limit=2)[0])
	slist = []
	for root, subdirs, files in os.walk(directory):
			for sfile in files:
				slist.append(os.path.join(root, sfile))
	return slist

def list_dirs(directory):
	message.sub_traceback(traceback.extract_stack(limit=2)[0])
	slist = []
	for root, subdirs, files in os.walk(directory):
			for sdir in subdirs:
				slist.append(os.path.join(root, sdir))
	return slist

def chroot_exec(command, prepare=True, mount=True, output=False):
	message.sub_traceback(traceback.extract_stack(limit=2)[0])
	real_root = os.open('/', os.O_RDONLY)
	try:
		# FIXME: /proc/mtab
		if prepare:
			if os.path.isfile('/etc/resolv.conf'):
				copy_file('/etc/resolv.conf', configparser.FILESYSTEM_DIR + '/etc/resolv.conf')
		
		if mount:
			for s in ['/proc', '/dev', '/sys']:
				sdir = configparser.FILESYSTEM_DIR + s
				if not os.path.ismount(sdir):
					if not os.path.isdir(sdir):
						os.makedirs(sdir)
					subprocess.check_call([whereis('mount'), '--rbind', s, sdir])
					
		os.chroot(configparser.FILESYSTEM_DIR)
		os.chdir('/')
		if prepare:
			if not os.path.isfile('/etc/mtab'):
				os.symlink('/proc/mounts', '/etc/mtab')
		
		if output:
			output = get_output(command)
		else:
			subprocess.check_call(command)
	finally:
		os.fchdir(real_root)
		os.chroot(".")
		os.close(real_root)
		
		if mount:
			for s in ['/proc', '/dev', '/sys']:
				sdir = configparser.FILESYSTEM_DIR + s
				if os.path.ismount(sdir):
					subprocess.check_call([whereis('umount'), '--force', '--lazy', sdir])
		return output