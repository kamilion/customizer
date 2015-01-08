# -*- Mode: Python -*-
# vi:si:et:sw=4:sts=4:ts=4

# Copyright (c) 2001-2002, MetaSlash Inc.  All rights reserved.

"""
Object to hold information about functions.
Also contain a pseudo Python function object
"""

import string

_ARGS_ARGS_FLAG = 4
_KW_ARGS_FLAG = 8
_CO_FLAGS_MASK = _ARGS_ARGS_FLAG + _KW_ARGS_FLAG

class _ReturnValues:
    """
    I am a base class that can track return values.

    @ivar returnValues: tuple of (line number, stack item,
                                  index to next instruction)
    @type returnValues: tuple of (int, L{pychecker.Stack.Item}, int)
    """
    def __init__(self):
        self.returnValues = None

    def returnsNoValue(self):
        returnValues = self.returnValues
        # if unset, we don't know
        if returnValues is None:
            return 0
        # it's an empty list, that means no values
        if not returnValues:
            return 1
        # make sure each value is not None
        for rv in returnValues:
            if not rv[1].isNone():
                return 0
        return returnValues[-1][1].isImplicitNone()

class FakeCode :
    "This is a holder class for code objects (so we can modify them)"
    def __init__(self, code, varnames = None) :
        """
        @type  code: L{types.CodeType}
        """
        for attr in dir(code):
            try:
                setattr(self, attr, getattr(code, attr))
            except:
                pass
        if varnames is not None:
            self.co_varnames = varnames

class FakeFunction(_ReturnValues):
    """
    This is a holder class for turning non-scoped code (for example at
    module-global level, or generator expressions) into a function.
    
    Pretends to be a normal callable and can be used as constructor argument
    to L{Function}
    """

    def __init__(self, name, code, func_globals = {}, varnames = None) :
        _ReturnValues.__init__(self)
        self.func_name = self.__name__ = name
        self.func_doc  = self.__doc__  = "ignore"

        self.func_code = FakeCode(code, varnames)
        self.func_defaults = None
        self.func_globals = func_globals

    def __str__(self):
        return self.func_name

    def __repr__(self):
        return '%s from %r' % (self.func_name, self.func_code.co_filename)

class Function(_ReturnValues):
    """
    Class to hold all information about a function

    @ivar function:   the function to wrap
    @type function:   callable
    @ivar isMethod:   whether the callable is a method
    @type isMethod:   int (used as bool)
    @ivar minArgs:    the minimum number of arguments that should be passed to
                      this function
    @type minArgs:    int
    @ivar minArgs:    the maximum number of arguments that should be passed to
                      this function, or None in case of *args/unlimited
    @type maxArgs:    int or None
    @ivar supportsKW: whether the function supports keyword arguments.
    @type supportsKW: int (used as bool)
    """

    def __init__(self, function, isMethod=0):
        """
        @param function: the function to wrap
        @type  function: callable or L{FakeFunction}
        @param isMethod: whether the callable is a method
        @type  isMethod: int (used as bool)
        """
 
        _ReturnValues.__init__(self)

        self.function = function
        self.isMethod = isMethod
        # co_argcount is the number of positional arguments (including
        # arguments with default values)
        self.minArgs = self.maxArgs = function.func_code.co_argcount
        # func_defaults is a tuple containing default argument values for those
        # arguments that have defaults, or None if no arguments have a default
        # value
        if function.func_defaults is not None:
            self.minArgs = self.minArgs - len(function.func_defaults)
        # if function uses *args, there is no max # args
        try:
            # co_flags is an integer encoding a number of flags for the
            # interpreter.
            if function.func_code.co_flags & _ARGS_ARGS_FLAG != 0:
                self.maxArgs = None
            self.supportsKW = function.func_code.co_flags & _KW_ARGS_FLAG
        except AttributeError:
            # this happens w/Zope
            self.supportsKW = 0

    def __str__(self):
        return self.function.func_name

    def __repr__(self):
        # co_filename is the filename from which the code was compiled
        # co_firstlineno is the first line number of the function
        return '<%s from %r:%d>' % (self.function.func_name,
                                    self.function.func_code.co_filename,
                                    self.function.func_code.co_firstlineno)

    def arguments(self):
        """
        @returns: a list of argument names to this function
        @rtype:   list of str
        """
        # see http://docs.python.org/reference/datamodel.html#types
        # for more info on func_code
        # co_argcount is the number of positional arguments (including
        # arguments with default values)
        numArgs = self.function.func_code.co_argcount
        if self.maxArgs is None:
            # co_varnames has the name of the *args variable after the
            # positional arguments
            numArgs = numArgs + 1
        if self.supportsKW:
            # co_varnames has the name of the **kwargs variable after the
            # positional arguments and *args variable
            numArgs = numArgs + 1
        # co_varnames is a tuple containing the names of the local variables
        # (starting with the argument names)
        # FIXME: a generator seems to have .0 as the first member here,
        #        and then the generator variable as the second.
        #        should we special-case that here ?
        return self.function.func_code.co_varnames[:numArgs]
        
    def isParam(self, name):
        """
        @type  name: str

        @returns: Whether the given name is the name of an argument to the
                  function
        @rtype:   bool
        """
        return name in self.arguments()

    def isStaticMethod(self):
        return self.isMethod and isinstance(self.function, type(create_fake))

    def isClassMethod(self):
        try:
            return self.isMethod and self.function.im_self is not None
        except AttributeError:
            return 0

    def defaultValue(self, name):
        """
        @type  name: str

        @returns: the default value for the function parameter with the given
                  name.
        """
        func_code = self.function.func_code
        arg_names = list(func_code.co_varnames[:func_code.co_argcount])
        i = arg_names.index(name)
        if i < self.minArgs:
            raise ValueError
        return self.function.func_defaults[i - self.minArgs]

    def varArgName(self):
        """
        @returns: the name of the *args parameter of the function.
        @rtype:   str
        """
        if self.maxArgs is not None:
            return None
        func_code = self.function.func_code
        return func_code.co_varnames[func_code.co_argcount]

def create_fake(name, code, func_globals = {}, varnames = None) :
    return Function(FakeFunction(name, code, func_globals, varnames))

def create_from_file(file, filename, module):
    """
    @type  filename: str

    @returns: a function that represents the __main__ entry point, if
              there was a file
    @rtype: L{Function}
    """
    if file is None:
        return create_fake(filename, compile('', filename, 'exec'))

    # Make sure the file is at the beginning
    #   if python compiled the file, it will be at the end
    file.seek(0)

    # Read in the source file, see py_compile.compile() for games w/src str
    codestr = file.read()
    codestr = string.replace(codestr, "\r\n", "\n")
    codestr = string.replace(codestr, "\r", "\n")
    if codestr and codestr[-1] != '\n':
        codestr = codestr + '\n'
    code = compile(codestr, filename, 'exec')
    return Function(FakeFunction('__main__', code, module.__dict__))

def _co_flags_equal(o1, o2) :
    return (o1.co_flags & _CO_FLAGS_MASK) == (o2.co_flags & _CO_FLAGS_MASK)
    
def same_signature(func, object) :
    '''Return a boolean value if the <func> has the same signature as
       a function with the same name in <object> (ie, an overriden method)'''

    try :
        baseMethod = getattr(object, func.func_name)
        base_func_code = baseMethod.im_func.func_code
    except AttributeError :
        return 1

    return _co_flags_equal(base_func_code, func.func_code) and \
           base_func_code.co_argcount == func.func_code.co_argcount

