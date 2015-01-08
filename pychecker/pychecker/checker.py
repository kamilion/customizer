#!/usr/bin/env python
# -*- Mode: Python -*-
# vi:si:et:sw=4:sts=4:ts=4

# Copyright (c) 2001-2004, MetaSlash Inc.  All rights reserved.
# Portions Copyright (c) 2005, Google, Inc.  All rights reserved.

"""
Check python source code files for possible errors and print warnings

Contact Info:
  http://pychecker.sourceforge.net/
  pychecker-list@lists.sourceforge.net
"""

import string
import types
import sys
import imp
import os
import glob

# see __init__.py for meaning, this must match the version there
LOCAL_MAIN_VERSION = 3


def setupNamespace(path) :
    # remove pychecker if it's the first component, it needs to be last
    if sys.path[0][-9:] == 'pychecker' :
        del sys.path[0]

    # make sure pychecker is last in path, so we can import
    checker_path = os.path.dirname(os.path.dirname(path))
    if checker_path not in sys.path :
        sys.path.append(checker_path)


def setupSysPathForDevelopment():
    import pychecker
    this_module = sys.modules[__name__]
    # in 2.2 and older, this_module might not have __file__ at all
    if not hasattr(this_module, '__file__'):
        return
    this_path = os.path.normpath(os.path.dirname(this_module.__file__))
    pkg_path = os.path.normpath(os.path.dirname(pychecker.__file__))
    if pkg_path != this_path:
        # pychecker was probably found in site-packages, insert this
        # directory before the other one so we can do development and run
        # our local version and not the version from site-packages.
        pkg_dir = os.path.dirname(pkg_path)
        i = 0
        for p in sys.path:
            if os.path.normpath(p) == pkg_dir:
                sys.path.insert(i-1, os.path.dirname(this_path))
                break
            i = i + 1
    del sys.modules['pychecker']


if __name__ == '__main__' :
    setupNamespace(sys.argv[0])
    setupSysPathForDevelopment()

from pychecker import utils
from pychecker import printer
from pychecker import warn
from pychecker import OP
from pychecker import Config
from pychecker import function
from pychecker import msgs
from pychecker import pcmodules
from pychecker.Warning import Warning

_cfg = None

_VERSION_MISMATCH_ERROR = '''
There seem to be two versions of PyChecker being used.
One is probably in python/site-packages, the other in a local directory.
If you want to run the local version, you must remove the version
from site-packages.  Or you can install the current version
by doing python setup.py install.
'''

def cfg() :
    return utils.cfg()

def _flattenList(list) :
    "Returns a list which contains no lists"

    new_list = []
    for element in list :
        if type(element) == types.ListType :
            new_list.extend(_flattenList(element))
        else :
            new_list.append(element)

    return new_list

def getModules(arg_list) :
    """
    arg_list is a list of arguments to pychecker; arguments can represent
    a module name, a filename, or a wildcard file specification.

    Returns a list of (module name, dirPath) that can be imported, where
    dirPath is the on-disk path to the module name for that argument.

    dirPath can be None (in case the given argument is an actual module).
    """

    new_arguments = []
    for arg in arg_list :
        # is this a wildcard filespec? (necessary for windows)
        if '*' in arg or '?' in arg or '[' in arg :
            arg = glob.glob(arg)
        new_arguments.append(arg)

    PY_SUFFIXES = ['.py']
    PY_SUFFIX_LENS = [3]
    if _cfg.quixote:
        PY_SUFFIXES.append('.ptl')
        PY_SUFFIX_LENS.append(4)
        
    modules = []
    for arg in _flattenList(new_arguments) :
        # if arg is an actual module, return None for the directory
        arg_dir = None
        # is it a .py file?
        for suf, suflen in zip(PY_SUFFIXES, PY_SUFFIX_LENS):
            if len(arg) > suflen and arg[-suflen:] == suf:
                arg_dir = os.path.dirname(arg)
                if arg_dir and not os.path.exists(arg) :
                    print 'File or pathname element does not exist: "%s"' % arg
                    continue

                module_name = os.path.basename(arg)[:-suflen]

                arg = module_name
        modules.append((arg, arg_dir))

    return modules


def getAllModules():
    """
    Returns a list of all modules that should be checked.

    @rtype: list of L{pcmodules.PyCheckerModule}
    """
    modules = []

    for module in pcmodules.getPCModules():
        if module.check:
            modules.append(module)

    return modules

_BUILTIN_MODULE_ATTRS = { 'sys': [ 'ps1', 'ps2', 'tracebacklimit', 
                                   'exc_type', 'exc_value', 'exc_traceback',
                                   'last_type', 'last_value', 'last_traceback',
                                 ],
                        }

def fixupBuiltinModules(needs_init=0):
    for moduleName in sys.builtin_module_names :
        # Skip sys since it will reset sys.stdout in IDLE and cause
        # stdout to go to the real console rather than the IDLE console.
        # FIXME: this breaks test42
        # if moduleName == 'sys':
        #     continue

        if needs_init:
            _ = pcmodules.PyCheckerModule(moduleName, 0)
        # builtin modules don't have a moduleDir
        module = pcmodules.getPCModule(moduleName)
        if module is not None :
            try :
                m = imp.init_builtin(moduleName)
            except ImportError :
                pass
            else :
                extra_attrs = _BUILTIN_MODULE_ATTRS.get(moduleName, [])
                module.attributes = [ '__dict__' ] + dir(m) + extra_attrs


def _printWarnings(warnings, stream=None):
    if stream is None:
        stream = sys.stdout
    
    warnings.sort()
    lastWarning = None
    for warning in warnings :
        if lastWarning is not None:
            # ignore duplicate warnings
            if cmp(lastWarning, warning) == 0:
                continue
            # print blank line between files
            if lastWarning.file != warning.file:
                stream.write("\n")

        lastWarning = warning
        warning.output(stream, removeSysPath=True)


class NullModule:
    def __getattr__(self, unused_attr):
        return None

def install_ignore__import__():

    _orig__import__ = None

    def __import__(name, globals=None, locals=None, fromlist=None):
        if globals is None:
            globals = {}
        if locals is None:
            locals = {}
        if fromlist is None:
            fromlist = ()

        try:
            pymodule = _orig__import__(name, globals, locals, fromlist)
        except ImportError:
            pymodule = NullModule()
            if not _cfg.quiet:
                modname = '.'.join((name,) + fromlist)
                sys.stderr.write("Can't import module: %s, ignoring.\n" % modname)
        return pymodule

    # keep the orig __import__ around so we can call it
    import __builtin__
    _orig__import__ = __builtin__.__import__
    __builtin__.__import__ = __import__

def processFiles(files, cfg=None, pre_process_cb=None):
    """
    @type  files:          list of str
    @type  cfg:            L{Config.Config}
    @param pre_process_cb: callable notifying of module name, filename
    @type  pre_process_cb: callable taking (str, str)
    """
    
    warnings = []

    # insert this here, so we find files in the local dir before std library
    if sys.path[0] != '' :
        sys.path.insert(0, '')

    # ensure we have a config object, it's necessary
    global _cfg
    if cfg is not None:
        _cfg = cfg
    elif _cfg is None:
        _cfg = Config.Config()

    if _cfg.ignoreImportErrors:
        install_ignore__import__()

    utils.initConfig(_cfg)

    utils.debug('Processing %d files' % len(files))

    for file, (moduleName, moduleDir) in zip(files, getModules(files)):
        if callable(pre_process_cb):
            pre_process_cb("module %s (%s)" % (moduleName, file))

        # create and load the PyCheckerModule, tricking sys.path temporarily
        oldsyspath = sys.path[:]
        sys.path.insert(0, moduleDir)
        pcmodule = pcmodules.PyCheckerModule(moduleName, moduleDir=moduleDir)
        loaded = pcmodule.load()
        sys.path = oldsyspath

        if not loaded:
            w = Warning(pcmodule.filename(), 1,
                        msgs.Internal("NOT PROCESSED UNABLE TO IMPORT"))
            warnings.append(w)

    utils.debug('Processed %d files' % len(files))

    utils.popConfig()

    return warnings

# only used by TKInter options.py
def getWarnings(files, cfg = None, suppressions = None):
    warnings = processFiles(files, cfg)
    fixupBuiltinModules()
    return warnings + warn.find(getAllModules(), _cfg, suppressions)


def _print_processing(name) :
    if not _cfg.quiet :
        sys.stderr.write("Processing %s...\n" % name)


def main(argv) :
    __pychecker__ = 'no-miximport'
    import pychecker
    if LOCAL_MAIN_VERSION != pychecker.MAIN_MODULE_VERSION :
        sys.stderr.write(_VERSION_MISMATCH_ERROR)
        sys.exit(100)

    # remove empty arguments
    argv = filter(None, argv)
        
    # if the first arg starts with an @, read options from the file
    # after the @ (this is mostly for windows)
    if len(argv) >= 2 and argv[1][0] == '@':
        # read data from the file
        command_file = argv[1][1:]
        try:
            f = open(command_file, 'r')
            command_line = f.read()
            f.close()
        except IOError, err:
            sys.stderr.write("Unable to read commands from file: %s\n  %s\n" % \
                             (command_file, err))
            sys.exit(101)

        # convert to an argv list, keeping argv[0] and the files to process
        argv = argv[:1] + string.split(command_line) + argv[2:]
 
    global _cfg
    _cfg, files, suppressions = Config.setupFromArgs(argv[1:])
    utils.initConfig(_cfg)
    if not files :
        return 0

    # Now that we've got the args, update the list of evil C objects
    for evil_doer in _cfg.evil:
        pcmodules.EVIL_C_OBJECTS[evil_doer] = None

    # insert this here, so we find files in the local dir before std library
    sys.path.insert(0, '')

    utils.debug('main: Finding import warnings')
    importWarnings = processFiles(files, _cfg, _print_processing)
    utils.debug('main: Found %d import warnings' % len(importWarnings))

    fixupBuiltinModules()
    if _cfg.printParse :
        for module in getAllModules() :
            printer.module(module)

    utils.debug('main: Finding warnings')
    # suppressions is a tuple of suppressions, suppressionRegexs dicts
    warnings = warn.find(getAllModules(), _cfg, suppressions)
    utils.debug('main: Found %d warnings' % len(warnings))

    if not _cfg.quiet :
        print "\nWarnings...\n"
    if warnings or importWarnings :
        _printWarnings(importWarnings + warnings)
        return 1

    if not _cfg.quiet :
        print "None"
    return 0


# FIXME: this is a nasty side effect for import checker
if __name__ == '__main__' :
    try :
        sys.exit(main(sys.argv))
    except Config.UsageError :
        sys.exit(127)

else :
    _orig__import__ = None
    _suppressions = None
    _warnings_cache = {}

    def _get_unique_warnings(warnings):
        for i in range(len(warnings)-1, -1, -1):
            w = warnings[i].format()
            if _warnings_cache.has_key(w):
                del warnings[i]
            else:
                _warnings_cache[w] = 1
        return warnings

    def __import__(name, globals=None, locals=None, fromlist=None):
        if globals is None:
            globals = {}
        if locals is None:
            locals = {}
        if fromlist is None:
            fromlist = []

        check = not sys.modules.has_key(name) and name[:10] != 'pychecker.'
        pymodule = _orig__import__(name, globals, locals, fromlist)
        if check :
            try :
                # FIXME: can we find a good moduleDir ?
                module = pcmodules.PyCheckerModule(pymodule.__name__)
                if module.initModule(pymodule):
                    warnings = warn.find([module], _cfg, _suppressions)
                    _printWarnings(_get_unique_warnings(warnings))
                else :
                    print 'Unable to load module', pymodule.__name__
            except Exception:
                name = getattr(pymodule, '__name__', utils.safestr(pymodule))
                # FIXME: can we use it here ?
                utils.importError(name)

        return pymodule

    def _init() :
        global _cfg, _suppressions, _orig__import__

        args = string.split(os.environ.get('PYCHECKER', ''))
        _cfg, files, _suppressions = Config.setupFromArgs(args)
        utils.initConfig(_cfg)
        fixupBuiltinModules(1)

        # keep the orig __import__ around so we can call it
        import __builtin__
        _orig__import__ = __builtin__.__import__
        __builtin__.__import__ = __import__

    if not os.environ.get('PYCHECKER_DISABLED') :
        _init()
