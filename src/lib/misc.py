#!/usr/bin/python2

import os, sys, re, shutil, urllib2, tarfile, gzip, subprocess, traceback

import lib.message as message
import lib.configparser as configparser

def check_uid():
	message.sub_traceback(traceback.extract_stack(limit=2)[0])
	if os.geteuid() == 0:
		return True
	return False

def whereis(program):
    message.sub_traceback(traceback.extract_stack(limit=2)[0])
    for path in os.environ.get('PATH', '').split(':'):
        if os.path.isfile(os.path.join(path, program)):
            return os.path.join(path, program)
    return None

''' Variables operations '''
def strip_list(string):
    message.sub_traceback(traceback.extract_stack(limit=2)[0])
    chars = ['[', ']', "'", ',']
    for char in chars:
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
            copytree(s, d, symlinks, ignore)
        else:
            if not os.path.exists(d) or os.stat(src).st_mtime - os.stat(dst).st_mtime > 1:
                shutil.copy2(s, d)

def move_dir(src, dst):
    message.sub_traceback(traceback.extract_stack(limit=2)[0])
    for src_dir, dirs, files in os.walk(src, topdown=True, onerror=None, followlinks=False):
		dst_dir = src_dir.replace(src, dst)
		if not os.path.exists(dst_dir):
			os.mkdir(dst_dir)
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

''' File operations '''
def mime_file(sfile):
	message.sub_traceback(traceback.extract_stack(limit=2)[0])
	# return mimetypes.guess_type(file)
	return get_output(['file', '--brief', '--mime-type', sfile])

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
	content = wfile.write(content)
	wfile.close()

''' System operations '''
def get_output(command):
	message.sub_traceback(traceback.extract_stack(limit=2)[0])
	pipe = subprocess.Popen(command, stdout=subprocess.PIPE)
	return pipe.communicate()[0].strip()

''' Misc '''
def search_string(string, string2, exact=False, escape=True):
	message.sub_traceback(traceback.extract_stack(limit=2)[0])
	if exact == True and escape == True:
		return re.search(re.escape(string) + '\\Z|' + re.escape(string) + '\\s', strip_list(string2))
	elif exact == True:
		return re.search(string + '\\Z|' + string + '\\s', strip_list(string2))
	elif escape == True:
		return re.search(re.escape(string), strip_list(string2))
	else:
		return re.search(string, str(string2))

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

def chroot_exec(command):
	message.sub_traceback(traceback.extract_stack(limit=2)[0])
	try:
		real_root = os.open("/", os.O_RDONLY)
		for s in ['/proc', '/dev', '/sys']:
			sdir = configparser.FILESYSTEM_DIR + s
			if not os.path.ismount(sdir):
				if not os.path.isdir(sdir):
					os.makedirs(sdir)
				subprocess.check_call(['mount', '--rbind', s, sdir])
		os.chroot(configparser.FILESYSTEM_DIR)
		subprocess.check_call(command)
	finally:
		os.fchdir(real_root)
		os.chroot(".")
		os.close(real_root)
		for s in ['/proc', '/dev', '/sys']:
			sdir = configparser.FILESYSTEM_DIR + s
			if os.path.ismount(sdir):
				subprocess.check_call(['umount', '--force', '--lazy', sdir])