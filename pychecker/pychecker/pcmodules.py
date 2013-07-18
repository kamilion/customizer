# -*- Mode: Python -*-
# vi:si:et:sw=4:sts=4:ts=4

"""
Track loaded PyCheckerModules together with the directory they were loaded from.
This allows us to differentiate between loaded modules with the same name
but from different paths, in a way that sys.modules doesn't do.
"""

import re
import sys
import imp
import types
import string

from pychecker import utils, function, Config, OP

# Constants
_DEFAULT_MODULE_TOKENS = ('__builtins__', '__doc__', '__file__', '__name__',
                          '__path__')
_DEFAULT_CLASS_TOKENS = ('__doc__', '__name__', '__module__')

# When using introspection on objects from some C extension modules,
# the interpreter will crash.  Since pychecker exercises these bugs we
# need to blacklist the objects and ignore them.  For more info on how
# to determine what object is causing the crash, search for this
# comment below (ie, it is also several hundred lines down):
#
#     README if interpreter is crashing:

# FIXME: the values should indicate the versions of these modules
# that are broken.  We shouldn't ignore good modules.

EVIL_C_OBJECTS = {
    'matplotlib.axes.BinOpType': None,  # broken on versions <= 0.83.2

    # broken on versions at least 2.5.5 up to 2.6
    'wx.TheClipboard': None,
    'wx._core.TheClipboard': None,
    'wx._misc.TheClipboard': None,
  }


__pcmodules = {}

def _filterDir(object, ignoreList):
    """
    Return a list of attribute names of an object, excluding the ones
    in ignoreList.

    @type  ignoreList: list of str

    @rtype: list of str
    """

    tokens = dir(object)

    for token in ignoreList:
        if token in tokens:
            tokens.remove(token)

    return tokens

def _getClassTokens(c):
    return _filterDir(c, _DEFAULT_CLASS_TOKENS)



def _getPyFile(filename):
    """Return the file and '.py' filename from a filename which could
    end with .py, .pyc, or .pyo"""

    if filename[-1] in 'oc' and filename[-4:-1] == '.py':
        return filename[:-1]
    return filename

def _getModuleTokens(m):
    return _filterDir(m, _DEFAULT_MODULE_TOKENS)

class Variable:
    "Class to hold all information about a variable"

    def __init__(self, name, type):
        """
        @param name: name of the variable
        @type  name: str
        @param type: type of the variable
        @type  type: type
        """
        self.name = name
        self.type = type
        self.value = None

    def __str__(self) :
        return self.name

    __repr__ = utils.std_repr

class Class:
    """
    Class to hold all information about a class.

    @ivar name:        name of class
    @type name:        str
    @ivar classObject: the object representing the class
    @type classObject: class
    @ivar module:      the module where the class is defined
    @type module:      module
    @ivar ignoreAttrs: whether to ignore this class's attributes when checking
                       attributes.  Can be set because of a bad __getattr__
                       or because the module this class comes from is
                       blacklisted.
    @type ignoreAttrs: int (used as bool)
    @type methods:     dict
    @type members:     dict of str -> type
    @type memberRefs:  dict
    @type statics:     dict
    @type lineNums:    dict
    """

    def __init__(self, name, pcmodule):
        """
        @type name:     str
        @type pcmodule: L{PyCheckerModule}
        """
        self.name = name
        module = pcmodule.module
        self.classObject = getattr(module, name)

        modname = getattr(self.classObject, '__module__', None)
        if modname is None:
            # hm, some ExtensionClasses don't have a __module__ attribute
            # so try parsing the type output
            typerepr = repr(type(self.classObject))
            mo = re.match("^<type ['\"](.+)['\"]>$", typerepr)
            if mo:
                modname = ".".join(mo.group(1).split(".")[:-1])

        # TODO(nnorwitz): this check for __name__ might not be necessary
        # any more.  Previously we checked objects as if they were classes.
        # This problem is fixed by not adding objects as if they are classes.

        # zope.interface for example has Provides and Declaration that
        # look a lot like class objects but do not have __name__
        if not hasattr(self.classObject, '__name__'):
            if modname not in utils.cfg().blacklist:
                sys.stderr.write("warning: no __name__ attribute "
                                 "for class %s (module name: %s)\n"
                                 % (self.classObject, modname))
            self.classObject.__name__ = name
        # later pychecker code uses this
        self.classObject__name__ = self.classObject.__name__

        self.module = sys.modules.get(modname)
        # if the pcmodule has moduleDir, it means we processed it before,
        # and deleted it from sys.modules
        if not self.module and pcmodule.moduleDir is None:
            self.module = module
            if modname not in utils.cfg().blacklist:
                sys.stderr.write("warning: couldn't find real module "
                                 "for class %s (module name: %s)\n"
                                 % (self.classObject, modname))
        self.ignoreAttrs = 0
        self.methods = {}
        self.members = { '__class__': types.ClassType,
                         '__doc__': types.StringType,
                         '__dict__': types.DictType, }
        self.memberRefs = {}
        self.statics = {}
        self.lineNums = {}

    def __str__(self) :
        return self.name

    __repr__ = utils.std_repr

    def getFirstLine(self) :
        "Return first line we can find in THIS class, not any base classes"

        lineNums = []
        classDir = dir(self.classObject)
        for m in self.methods.values() :
            if m != None and m.function.func_code.co_name in classDir:
                lineNums.append(m.function.func_code.co_firstlineno)
        if lineNums :
            return min(lineNums)
        return 0

    def allBaseClasses(self, c = None) :
        "Return a list of all base classes for this class and its subclasses"

        baseClasses = []
        if c == None :
            c = self.classObject
        for base in getattr(c, '__bases__', None) or ():
            baseClasses = baseClasses + [ base ] + self.allBaseClasses(base)
        return baseClasses

    def __getMethodName(self, func_name, className = None) :
        if func_name[0:2] == '__' and func_name[-2:] != '__' :
            if className == None :
                className = self.name
            if className[0] != '_' :
                className = '_' + className
            func_name = className + func_name
        return func_name

    def addMethod(self, methodName, method=None):
        """
        Add the given method to this class by name.

        @type methodName: str
        @type method:     method or None
        """
        if not method:
            self.methods[methodName] = None
        else :
            self.methods[methodName] = function.Function(method, 1)
                 
    def addMethods(self, classObject):
        """
        Add all methods for this class object to the class.

        @param classObject: the class object to add methods from.
        @type  classObject: types.ClassType (classobj)
        """
        for classToken in _getClassTokens(classObject):
            token = getattr(classObject, classToken, None)
            if token is None:
                continue

            # Looks like a method.  Need to code it this way to
            # accommodate ExtensionClass and Python 2.2.  Yecchh.
            if (hasattr(token, "func_code") and
                hasattr(token.func_code, "co_argcount")): 
                self.addMethod(token.__name__, method=token)

            elif hasattr(token, '__get__') and \
                 not hasattr(token, '__set__') and \
                 type(token) is not types.ClassType:
                self.addMethod(getattr(token, '__name__', classToken))
            else:
                self.members[classToken] = type(token)
                self.memberRefs[classToken] = None

        self.cleanupMemberRefs()
        # add standard methods
        for methodName in ('__class__', ):
            self.addMethod(methodName)

    def addMembers(self, classObject) :
        if not utils.cfg().onlyCheckInitForMembers :
            for classToken in _getClassTokens(classObject) :
                method = getattr(classObject, classToken, None)
                if type(method) == types.MethodType :
                    self.addMembersFromMethod(method.im_func)
        else:
            try:
                self.addMembersFromMethod(classObject.__init__.im_func)
            except AttributeError:
                pass

    def addMembersFromMethod(self, method) :
        if not hasattr(method, 'func_code') :
            return

        func_code, code, i, maxCode, extended_arg = OP.initFuncCode(method)
        stack = []
        while i < maxCode :
            op, oparg, i, extended_arg = OP.getInfo(code, i, extended_arg)
            if op >= OP.HAVE_ARGUMENT :
                operand = OP.getOperand(op, func_code, oparg)
                if OP.LOAD_CONST(op) or OP.LOAD_FAST(op) or OP.LOAD_GLOBAL(op):
                    stack.append(operand)
                elif OP.LOAD_DEREF(op):
                    try:
                        operand = func_code.co_cellvars[oparg]
                    except IndexError:
                        index = oparg - len(func_code.co_cellvars)
                        operand = func_code.co_freevars[index]
                    stack.append(operand)
                elif OP.STORE_ATTR(op) :
                    if len(stack) > 0 :
                        if stack[-1] == utils.cfg().methodArgName:
                            value = None
                            if len(stack) > 1 :
                                value = type(stack[-2])
                            self.members[operand] = value
                            self.memberRefs[operand] = None
                        stack = []

        self.cleanupMemberRefs()

    def cleanupMemberRefs(self) :
        try :
            del self.memberRefs[Config.CHECKER_VAR]
        except KeyError :
            pass

    def abstractMethod(self, m):
        """Return 1 if method is abstract, None if not
           An abstract method always raises an exception.
        """
        if not self.methods.get(m, None):
            return None
        funcCode, codeBytes, i, maxCode, extended_arg = \
                   OP.initFuncCode(self.methods[m].function)
        # abstract if the first opcode is RAISE_VARARGS and it raises
        # NotImplementedError
        arg = ""
        while i < maxCode:
            op, oparg, i, extended_arg = OP.getInfo(codeBytes, i, extended_arg)
            if OP.LOAD_GLOBAL(op):
                arg = funcCode.co_names[oparg]
            elif OP.RAISE_VARARGS(op):
                # if we saw NotImplementedError sometime before the raise
                # assume it's related to this raise stmt
                return arg == "NotImplementedError"
            if OP.conditional(op):
                break
        return None

    def isAbstract(self):
        """Return the method names that make a class abstract.
           An abstract class has at least one abstract method."""
        result = []
        for m in self.methods.keys():
            if self.abstractMethod(m):
                result.append(m)
        return result


class PyCheckerModule:
    """
    Class to hold all information for a module

    @ivar module:         the module wrapped by this PyCheckerModule
    @type module:         module
    @ivar moduleName:     name of the module
    @type moduleName:     str
    @ivar moduleDir:      if specified, the directory where the module can
                          be loaded from; allows discerning between modules
                          with the same name in a different directory.
                          Note that moduleDir can be the empty string, if
                          the module being tested lives in the current working
                          directory.
    @type moduleDir:      str
    @ivar variables:      dict of variable name -> Variable
    @type variables:      dict of str -> L{Variable}
    @ivar functions:      dict of function name -> function
    @type functions:      dict of str -> L{function.Function}
    @ivar classes:        dict of class name -> class
    @type classes:        dict of str -> L{Class}
    @ivar modules:        dict of module name -> module
    @type modules:        dict of str -> L{PyCheckerModule}
    @ivar moduleLineNums: mapping of the module's nameds/operands to the
                          filename and linenumber where they are created
    @type moduleLineNums: dict of str -> (str, int)
    @type mainCode:       L{function.Function}
    @ivar check:          whether this module should be checked
    @type check:          int (used as bool)
    """

    def __init__(self, moduleName, check=1, moduleDir=None):
        """
        @param moduleName: name of the module
        @type  moduleName: str
        @param check:      whether this module should be checked
        @type  check:      int (used as bool)
        @param moduleDir:  if specified, the directory where the module can
                           be loaded from; allows discerning between modules
                           with the same name in a different directory.
                           Note that moduleDir can be the empty string, if
                           the module being tested lives in the current working
                           directory.
        @type  moduleDir:  str
        """
        self.module = None
        self.moduleName = moduleName
        self.moduleDir = moduleDir
        self.variables = {}
        self.functions = {}
        self.classes = {}
        self.modules = {}
        self.moduleLineNums = {}
        self.attributes = [ '__dict__' ]
        self.mainCode = None
        self.check = check
        # key on a combination of moduleName and moduleDir so we have separate
        # entries for modules with the same name but in different directories
        addPCModule(self)

    def __str__(self):
        return self.moduleName

    __repr__ = utils.std_repr

    def addVariable(self, var, varType):
        """
        @param var:     name of the variable
        @type  var:     str
        @param varType: type of the variable
        @type  varType: type
        """
        
        self.variables[var] = Variable(var, varType)

    def addFunction(self, func):
        """
        @type  func: callable
        """
        self.functions[func.__name__] = function.Function(func)

    def __addAttributes(self, c, classObject) :
        for base in getattr(classObject, '__bases__', None) or ():
            self.__addAttributes(c, base)
        c.addMethods(classObject)
        c.addMembers(classObject)

    def addClass(self, name):
        self.classes[name] = c = Class(name, self)
        try:
            objName = utils.safestr(c.classObject)
        except TypeError:
            # this can happen if there is a goofy __getattr__
            c.ignoreAttrs = 1
        else:
            packages = string.split(objName, '.')
            c.ignoreAttrs = packages[0] in utils.cfg().blacklist
        if not c.ignoreAttrs :
            self.__addAttributes(c, c.classObject)

    def addModule(self, name, moduleDir=None) :
        module = getPCModule(name, moduleDir)
        if module is None :
            self.modules[name] = module = PyCheckerModule(name, 0)
            if imp.is_builtin(name) == 0:
                module.load()
            else :
                globalModule = globals().get(name)
                if globalModule :
                    module.attributes.extend(dir(globalModule))
        else :
            self.modules[name] = module

    def filename(self) :
        try :
            filename = self.module.__file__
        except AttributeError :
            filename = self.moduleName
            # FIXME: we're blindly adding .py, but it might be something else.
            if self.moduleDir:
                filename = self.moduleDir + '/' + filename + '.py'

        return _getPyFile(filename)

    def load(self):
        try :
            # there's no need to reload modules we already have if no moduleDir
            # is specified for this module
            # NOTE: self.moduleDir can be '' if the module tested lives in
            # the current working directory
            if self.moduleDir is None:
                module = sys.modules.get(self.moduleName)
                if module:
                    pcmodule = getPCModule(self.moduleName)
                    if not pcmodule.module:
                        return self._initModule(module)
                    return 1

            return self._initModule(self.setupMainCode())
        except (SystemExit, KeyboardInterrupt):
            exc_type, exc_value, exc_tb = sys.exc_info()
            raise exc_type, exc_value
        except:
            utils.importError(self.moduleName, self.moduleDir)
            return utils.cfg().ignoreImportErrors

    def initModule(self, module) :
        if not self.module:
            filename = _getPyFile(module.__file__)
            if string.lower(filename[-3:]) == '.py':
                try:
                    handle = open(filename)
                except IOError:
                    pass
                else:
                    self._setupMainCode(handle, filename, module)
            return self._initModule(module)
        return 1

    def _initModule(self, module):
        self.module = module
        self.attributes = dir(self.module)

        # interpret module-specific suppressions
        pychecker_attr = getattr(module, Config.CHECKER_VAR, None)
        if pychecker_attr is not None :
            utils.pushConfig()
            utils.updateCheckerArgs(pychecker_attr, 'suppressions', 0, [])

        # read all tokens from the real module, and register them
        for tokenName in _getModuleTokens(self.module):
            if EVIL_C_OBJECTS.has_key('%s.%s' % (self.moduleName, tokenName)):
                continue

            # README if interpreter is crashing:
            # Change 0 to 1 if the interpretter is crashing and re-run.
            # Follow the instructions from the last line printed.
            if utils.cfg().findEvil:
                print "Add the following line to EVIL_C_OBJECTS or the string to evil in a config file:\n" \
                      "    '%s.%s': None, " % (self.moduleName, tokenName)

            token = getattr(self.module, tokenName)
            if isinstance(token, types.ModuleType) :
                # get the real module name, tokenName could be an alias
                self.addModule(token.__name__)
            elif isinstance(token, types.FunctionType) :
                self.addFunction(token)
            elif isinstance(token, types.ClassType) or \
                 hasattr(token, '__bases__') and \
                 issubclass(type(token), type):
                self.addClass(tokenName)
            else :
                self.addVariable(tokenName, type(token))

        if pychecker_attr is not None :
            utils.popConfig()
        return 1

    def setupMainCode(self):
        handle, filename, smt = utils.findModule(
            self.moduleName, self.moduleDir)
        # FIXME: if the smt[-1] == imp.PKG_DIRECTORY : load __all__
        # HACK: to make sibling imports work, we add self.moduleDir to sys.path
        # temporarily, and remove it later
        if self.moduleDir is not None:
            oldsyspath = sys.path[:]
            sys.path.insert(0, self.moduleDir)
        module = imp.load_module(self.moduleName, handle, filename, smt)
        if self.moduleDir is not None:
            sys.path = oldsyspath
            # to make sure that subsequent modules with the same moduleName
            # do not persist, and get their namespace clobbered, delete it
            del sys.modules[self.moduleName]

        self._setupMainCode(handle, filename, module)
        return module

    def _setupMainCode(self, handle, filename, module):
        try:
            self.mainCode = function.create_from_file(handle, filename, module)
        finally:
            if handle != None:
                handle.close()

    def getToken(self, name):
        """
        Looks up the given name in this module's namespace.

        @param name: the name of the token to look up in this module.

        @rtype: one of L{Variable}, L{function.Function}, L{Class},
                L{PyCheckerModule}, or None
        """
        if name in self.variables:
            return self.variables[name]
        elif name in self.functions:
            return self.functions[name]
        elif name in self.classes:
            return self.classes[name]
        elif name in self.modules:
            return self.modules[name]

        return None


def getPCModule(moduleName, moduleDir=None):
    """
    @type  moduleName: str
    @param moduleDir:  if specified, the directory where the module can
                       be loaded from; allows discerning between modules
                       with the same name in a different directory.
                       Note that moduleDir can be the empty string, if
                       the module being tested lives in the current working
                       directory.
    @type  moduleDir:  str

    @rtype: L{pychecker.checker.PyCheckerModule}
    """

    global __pcmodules
    return __pcmodules.get((moduleName, moduleDir), None)

def getPCModules():
    """
    @rtype: list of L{pychecker.checker.PyCheckerModule}
    """
    global __pcmodules
    return __pcmodules.values()

def addPCModule(pcmodule):
    """
    @type  pcmodule: L{pychecker.checker.PyCheckerModule}
    """
    global __pcmodules
    __pcmodules[(pcmodule.moduleName, pcmodule.moduleDir)] = pcmodule
