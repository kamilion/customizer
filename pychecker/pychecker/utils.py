# -*- Mode: Python -*-
# vi:si:et:sw=4:sts=4:ts=4

# Copyright (c) 2001-2004, MetaSlash Inc.  All rights reserved.

"""
Utility functions.
"""

import re
import sys
import os
import string
import copy
import imp
import traceback
import types

from pychecker import msgs
from pychecker import Config
from pychecker.Warning import Warning


VAR_ARGS_BITS = 8
MAX_ARGS_MASK = ((1 << VAR_ARGS_BITS) - 1)

INIT = '__init__'
LAMBDA = '<lambda>'
GENEXP = '<generator expression>'
GENEXP25 = '<genexpr>'

# number of instructions to check backwards if it was a return
BACK_RETURN_INDEX = 4


_cfg = []

def cfg() :
    return _cfg[-1]

def initConfig(cfg) :
    _cfg.append(cfg)

def pushConfig() :
    newCfg = copy.copy(cfg())
    _cfg.append(newCfg)

def popConfig() :
    del _cfg[-1]


def shouldUpdateArgs(operand) :
    return operand == Config.CHECKER_VAR

def updateCheckerArgs(argStr, func, lastLineNum, warnings):
    """
    @param argStr:      list of space-separated options, as passed
                        on the command line
                        e.g 'blacklist=wrongname initattr no-classdoc'
    @type  argStr:      str
    @param func:        'suppressions' or code object
    @type  func:        str or {function.FakeCode} or {types.CodeType}
    @param lastLineNum: the last line number of the given function;
                        compare to func.co_firstlineno if exists
    @type  lastLineNum: int or {types.CodeType}
    @param warnings:    list of warnings to append to
    @type  warnings:    list of L{Warning}

    @rtype:   int
    @returns: 1 if the arguments were invalid, 0 if ok.
    """
    try:
        argList = string.split(argStr)
        # if func is code, might trigger
        # TypeError: code.__cmp__(x,y) requires y to be a 'code', not a 'str'
        if argList and not type(func) == str:
            debug('func %r: pychecker args %r', func, argStr)
        # don't require long options to start w/--, we can add that for them
        for i in range(0, len(argList)):
            if argList[i][0] != '-':
                argList[i] = '--' + argList[i]

        cfg().processArgs(argList)
        return 1
    except Config.UsageError, detail:
        # this gets triggered when parsing a bad __pychecker__ declaration
        warn = Warning(func, lastLineNum, msgs.INVALID_CHECKER_ARGS % detail)
        warnings.append(warn)
        return 0
                       

def debug(formatString, *args):
    if cfg().debug:
        if args:
            if '%' in formatString:
                message = formatString % args
            else:
                args = [isinstance(a, str) and a or repr(a) for a in args]
                message = formatString + " " + " ".join(args)
        else:
            message = formatString
        print "DEBUG:", message


PYTHON_1_5 = 0x10502
PYTHON_2_0 = 0x20000
PYTHON_2_1 = 0x20100
PYTHON_2_2 = 0x20200
PYTHON_2_3 = 0x20300
PYTHON_2_4 = 0x20400
PYTHON_2_5 = 0x20500
PYTHON_2_6 = 0x20600
PYTHON_2_7 = 0x20700
PYTHON_3_0 = 0x30000

def pythonVersion() :
    return sys.hexversion >> 8

def startswith(s, substr) :
    "Ugh, supporting python 1.5 is a pain"
    return s[0:len(substr)] == substr

def endswith(s, substr) :
    "Ugh, supporting python 1.5 is a pain"
    return s[-len(substr):] == substr


# generic method that can be slapped into any class, thus the self parameter
def std_repr(self) :
    return "<%s at 0x%x: %s>" % (self.__class__.__name__, id(self), safestr(self))

try:
    unicode, UnicodeError
except NameError:
    class UnicodeError(Exception): pass

def safestr(value):
   try:
      return str(value)
   except UnicodeError:
      return unicode(value)


def _q_file(f):
    # crude hack!!!
    # imp.load_module requires a real file object, so we can't just
    # fiddle def lines and yield them
    import tempfile
    fd, newfname = tempfile.mkstemp(suffix=".py", text=True)
    newf = os.fdopen(fd, 'r+')
    os.unlink(newfname)
    for line in f:
        mat = re.match(r'(\s*def\s+\w+\s*)\[(html|plain)\](.*)', line)
        if mat is None:
            newf.write(line)
        else:
            newf.write(mat.group(1)+mat.group(3)+'\n')
    newf.seek(0)
    return newf

def _q_find_module(p, path):
    if not cfg().quixote:
        return imp.find_module(p, path)
    else:
        for direc in path:
            try:
                return imp.find_module(p, [direc])
            except ImportError:
                f = os.path.join(direc, p+".ptl")
                if os.path.exists(f):
                    return _q_file(file(f)), f, ('.ptl', 'U', 1)

def findModule(name, moduleDir=None) :
    """Returns the result of an imp.find_module(), ie, (file, filename, smt)
       name can be a module or a package name.  It is *not* a filename."""

    path = sys.path[:]
    if moduleDir:
        path.insert(0, moduleDir)

    packages = string.split(name, '.')
    for p in packages :
        # smt = (suffix, mode, type)
        handle, filename, smt = _q_find_module(p, path)
        if smt[-1] == imp.PKG_DIRECTORY :
            try :
                # package found - read path info from init file
                m = imp.load_module(p, handle, filename, smt)
            finally :
                if handle is not None :
                    handle.close()

            # importing xml plays a trick, which replaces itself with _xmlplus
            # both have subdirs w/same name, but different modules in them
            # we need to choose the real (replaced) version
            if m.__name__ != p :
                try :
                    handle, filename, smt = _q_find_module(m.__name__, path)
                    m = imp.load_module(p, handle, filename, smt)
                finally :
                    if handle is not None :
                        handle.close()

            new_path = m.__path__
            if type(new_path) == types.ListType :
                new_path = filename
            if new_path not in path :
                path.insert(1, new_path)
        elif smt[-1] != imp.PY_COMPILED:
            if p is not packages[-1] :
                if handle is not None :
                    handle.close()
                raise ImportError, "No module named %s" % packages[-1]
            return handle, filename, smt

    # in case we have been given a package to check
    return handle, filename, smt


def _getLineInFile(moduleName, moduleDir, linenum):
    line = ''
    handle, filename, smt = findModule(moduleName, moduleDir)
    if handle is None:
        return ''
    try:
        lines = handle.readlines()
        line = string.rstrip(lines[linenum - 1])
    except (IOError, IndexError):
        pass
    handle.close()
    return line

def importError(moduleName, moduleDir=None):
    exc_type, exc_value, tb = sys.exc_info()

    # First, try to get a nice-looking name for this exception type.
    exc_name = getattr(exc_type, '__name__', None)
    if not exc_name:
        # either it's a string exception or a user-defined exception class
        # show string or fully-qualified class name
        exc_name = safestr(exc_type)
        
    # Print a traceback, unless this is an ImportError.  ImportError is
    # presumably the most common import-time exception, so this saves
    # the clutter of a traceback most of the time.  Also, the locus of
    # the error is usually irrelevant for ImportError, so the lack of
    # traceback shouldn't be a problem.
    if exc_type is SyntaxError:
        # SyntaxErrors are special, we want to control how we format
        # the output and make it consistent for all versions of Python
        e = exc_value
        msg = '%s (%s, line %d)' % (e.msg, e.filename, e.lineno)
        line = _getLineInFile(moduleName, moduleDir, e.lineno)
        offset = e.offset
        if type(offset) is not types.IntType:
            offset = 0
        exc_value = '%s\n    %s\n   %s^' % (msg, line, ' ' * offset)
    elif exc_type is not ImportError:
        sys.stderr.write("  Caught exception importing module %s:\n" %
                         moduleName)

        try:
            tbinfo = traceback.extract_tb(tb)
        except:
            tbinfo = []
            sys.stderr.write("      Unable to format traceback\n")
        for filename, line, func, text in tbinfo[1:]:
            sys.stderr.write("    File \"%s\", line %d" % (filename, line))
            if func != "?":
                sys.stderr.write(", in %s()" % func)
            sys.stderr.write("\n")
            if text:
                sys.stderr.write("      %s\n" % text)

    # And finally print the exception type and value.
    # Careful formatting exc_value -- can fail for some user exceptions
    sys.stderr.write("  %s: " % exc_name)
    try:
        sys.stderr.write(safestr(exc_value) + '\n')
    except:
        sys.stderr.write('**error formatting exception value**\n')


