# -*- Mode: Python; test-case-name: test.test_pychecker_CodeChecks -*-
# vi:si:et:sw=4:sts=4:ts=4

# Copyright (c) 2001-2006, MetaSlash Inc.  All rights reserved.
# Portions Copyright (c) 2005, Google, Inc.  All rights reserved.

"""
Find warnings in byte code from Python source files.
"""

# For documentation about dispatcher arguments, look for
# dispatcher functions for operands

import keyword
import string
import types

from pychecker import msgs
from pychecker import utils
from pychecker import Warning
from pychecker import OP
from pychecker import Stack
from pychecker import python

__pychecker__ = 'no-argsused'


def cfg() :
    return utils.cfg()

def getFunctionArgErr(funcName, argCount, minArgs, maxArgs):
    """
    Check that the number of arguments given is correct according to
    the given minArgs and maxArgs.

    @type funcName:   str
    @type argCount:   int
    @ivar minArgs:    the minimum number of arguments that should be passed to
                      this function
    @type minArgs:    int
    @ivar minArgs:    the maximum number of arguments that should be passed to
                      this function, or None in case of *args/unlimited
    @type maxArgs:    int or None

    @rtype: L{msgs.WarningClass} or None
    """
    err = None

    if maxArgs == None:
        if argCount < minArgs :
            err = msgs.INVALID_ARG_COUNT2 % (funcName, argCount, minArgs)
    elif argCount < minArgs or argCount > maxArgs:
        if minArgs == maxArgs:
            err = msgs.INVALID_ARG_COUNT1 % (funcName, argCount, minArgs)
        else:
            err = msgs.INVALID_ARG_COUNT3 % (funcName, argCount, minArgs,
                maxArgs)

    return err

def _checkFunctionArgCount(code, func_name, argCount, minArgs, maxArgs,
                           objectReference=0):
    """
    @param objectReference: whether the first argument references self
    @type  objectReference: int (used as bool)
    """
    # there is an implied argument for object creation and self.xxx()
    # FIXME: this is where test44 fails
    if objectReference:
        minArgs = minArgs - 1
        if maxArgs is not None:
            maxArgs = maxArgs - 1

    err = getFunctionArgErr(func_name, argCount, minArgs, maxArgs)
    if err:
        code.addWarning(err)

def _checkFunctionArgs(code, func, objectReference, argCount, kwArgs,
                       checkArgCount=1):
    """
    @param code:            The code block containing the invocation of the
                            function to be checked
    @type  code:            L{Code}
    @param func:            The function to check the invocation against
    @type  func:            L{function.Function}
    @param objectReference: whether the first argument references self
    @type  objectReference: int (used as bool)
    @param checkArgCount:   whether the first argument references self
    @type  checkArgCount:   int (used as bool)
    """
    func_name = func.function.func_code.co_name
    if kwArgs :
        args_len = func.function.func_code.co_argcount
        arg_names = func.function.func_code.co_varnames[argCount:args_len]
        if argCount < args_len and kwArgs[0] in arg_names:
            if cfg().namedArgs :
                code.addWarning(msgs.FUNC_USES_NAMED_ARGS % func_name)

            # convert the named args into regular params, and really check
            while argCount < args_len and kwArgs and kwArgs[0] in arg_names:
                argCount = argCount + 1
                kwArgs = kwArgs[1:]
            _checkFunctionArgs(code, func, objectReference, argCount, kwArgs,
                               checkArgCount)
            return

        if not func.supportsKW :
            code.addWarning(msgs.FUNC_DOESNT_SUPPORT_KW % func_name)

    if checkArgCount:
        _checkFunctionArgCount(code, func_name, argCount,
                               func.minArgs, func.maxArgs, objectReference)

def _getReferenceFromModule(module, identifier):
    """
    Looks up the given identifier in the module.
    If it is a function, returns (function, None, 0)
    If it is a class instantiation, returns (__init__ function, class, 1)

    @type  module:     L{pychecker.checker.PyCheckerModule}
    @type  identifier: str

    @returns: a triple of:
              - the function object (which can be the __init__ for the class)
              - the class, if the identifier references a class
              - 0 if it was a function, 1 if it was a class
    @rtype:   triple of (function, class or None, int (as bool))
    """

    # if the identifier is in the list of module's functions, return
    # the function, with no class, and method 0
    func = module.functions.get(identifier, None)
    if func is not None:
        return func, None, 0

    # now look it up as a class instantiation
    c = module.classes.get(identifier, None)
    if c is not None :
        func = c.methods.get(utils.INIT, None)
        return func, c, 1

    # not found as either
    return None, None, 0

def _getFunction(module, stackValue):
    # FIXME: it's not clear to me if the above method really returns
    # whether the stack value is a constructor
    """
    Return (function, class, is_a_method) from the stack value

    @type  module:     L{pychecker.checker.PyCheckerModule}
    @type  stackValue: L{Stack.Item}

    @rtype: tuple of (function or None, class or None, int (as bool))
    """

    identifier = stackValue.data
    if type(identifier) == types.StringType:
        return _getReferenceFromModule(module, identifier)

    # find the module this references
    i, maxLen = 0, len(identifier)
    while i < maxLen :
        name = utils.safestr(identifier[i])
        if module.classes.has_key(name) or module.functions.has_key(name) :
            break
        refModule = module.modules.get(name, None)
        if refModule is not None :
            module = refModule
        else :
            return None, None, 0
        i = i + 1

    # if we got to the end, there is only modules, nothing we can do
    # we also can't handle if there is more than 2 items left
    if i >= maxLen or (i+2) < maxLen :
        return None, None, 0

    if (i+1) == maxLen :
        return _getReferenceFromModule(module, identifier[-1])

    # we can't handle self.x.y
    if (i+2) == maxLen and identifier[0] == cfg().methodArgName:
        return None, None, 0

    c = module.classes.get(identifier[-2], None)
    if c is None :
        return None, None, 0
    return c.methods.get(identifier[-1], None), c, 0

def _validateKwArgs(code, info, func_name, kwArgs):
    if len(info) < 4:
        code.addWarning(msgs.FUNC_DOESNT_SUPPORT_KW % func_name)
    elif not info[3]:
        return

    try:
        # info could be from a builtin method which means that
        # info[3] is not a list.
        dummy = info[3][0]
    except IndexError:
        return

    for arg in kwArgs:
        if arg not in info[3]:
            code.addWarning(msgs.FUNC_DOESNT_SUPPORT_KW_ARG % (func_name, arg))

def _checkBuiltin(code, loadValue, argCount, kwArgs, check_arg_count = 1) :
    returnValue = Stack.makeFuncReturnValue(loadValue, argCount)
    func_name = loadValue.data
    if loadValue.type == Stack.TYPE_GLOBAL :
        info = python.GLOBAL_FUNC_INFO.get(func_name, None)
        if info is not None :
            if func_name == 'input' and cfg().usesInput:
                code.addWarning(msgs.USES_INPUT)
            if cfg().constAttr and \
               ((func_name == 'setattr' and argCount >= 2) or 
                (func_name == 'getattr' and argCount == 2)):
                arg2 = code.stack[-argCount + 1]
                if arg2.const and not keyword.iskeyword(arg2.data):
                    # lambda with setattr and const is a common way of setting
                    # attributes, so allow it
                    if code.func.function.func_name != '<lambda>':
                        code.addWarning(msgs.USES_CONST_ATTR % func_name)

            if kwArgs:
                _validateKwArgs(code, info, func_name, kwArgs)
            elif check_arg_count :
                _checkFunctionArgCount(code, func_name, argCount,
                                       info[1], info[2])
            returnValue = Stack.Item(returnValue.data, info[0])
            returnValue.setStringType(info[0])
    elif type(func_name) == types.TupleType and len(func_name) <= 2 :
        objType = code.typeMap.get(utils.safestr(func_name[0]), [])
        if types.ListType in objType :
            try :
                if func_name[1] == 'append' and argCount > 1 :
                    code.addWarning(msgs.LIST_APPEND_ARGS % func_name[0])
                    check_arg_count = 0
            except AttributeError :
                # FIXME: why do we need to catch AttributeError???
                pass
        if len(objType) == 1 :
            # if it's a builtin, check method
            builtinType = python.BUILTIN_METHODS.get(objType[0])
            if builtinType is not None :
                methodInfo = builtinType.get(func_name[1])
                # set func properly
                if kwArgs :
                    _validateKwArgs(code, methodInfo, func_name[1], kwArgs)
                elif methodInfo :
                    returnValue = Stack.Item(func_name[1], methodInfo[0])
                    returnValue.setStringType(methodInfo[0])
                    if check_arg_count and methodInfo is not None :
                        _checkFunctionArgCount(code, func_name[1], argCount,
                                               methodInfo[1], methodInfo[2])

    return returnValue

_IMMUTABLE_LIST_METHODS = ('count', 'index',)
_IMMUTABLE_DICT_METHODS = ('copy', 'get', 'has_key',
                           'items', 'keys', 'values',
                           'iteritems', 'iterkeys', 'itervalues')

def _checkModifyDefaultArg(code, objectName, methodName=None) :
    try :
        value = code.func.defaultValue(objectName)
        objectType = type(value)
        if objectType in python.MUTABLE_TYPES :
            if objectType == types.DictType and \
               methodName in _IMMUTABLE_DICT_METHODS :
                return 
            if objectType == types.ListType and \
               methodName in _IMMUTABLE_LIST_METHODS :
                return
            code.addWarning(msgs.MODIFYING_DEFAULT_ARG % objectName)
    except ValueError :
        pass

def _isexception(object) :
    # FIXME: i have no idea why this function is necessary
    # it seems that the issubclass() should work, but it doesn't always

    if hasattr(object, 'type'):
        if object.type == types.TupleType:
        # if we have a tuple, we can't check the contents (not enough info)
##            for item in object.value:
##                if not _isexception(item):
##                    return 0
            return 1

    try:
        # try/except is necessary for globals like NotImplemented
        if issubclass(object, Exception) :
            return 1
        # Python 2.5 added a BaseException to the hierarchy.  That's
        # really what we need to check if it exists.
        if utils.pythonVersion() >= utils.PYTHON_2_5:
            if issubclass(object, BaseException):
                return 1
    except TypeError:
        return 0

    for c in object.__bases__ :
        if utils.startswith(utils.safestr(c), 'exceptions.') :
            return 1
        if len(c.__bases__) > 0 and _isexception(c) :
            return 1
    return 0

def _checkStringFind(code, loadValue):
    if len(loadValue.data) == 2 and loadValue.data[1] == 'find':
        try:
            if types.StringType in code.typeMap.get(loadValue.data[0], []):
                op = code.nextOpInfo()[0]
                if OP.IS_CONDITIONAL_JUMP(op) or OP.IS_NOT(op):
                    code.addWarning(msgs.BAD_STRING_FIND)
        except TypeError:
            # we don't care if loadValue.data[0] is not hashable
            pass

def _checkAbstract(refClass, code, name):
    name_list = refClass.isAbstract()
    if name_list:
        name_list.sort()
        names = string.join(name_list, ", ")
        code.addWarning(msgs.METHODS_NEED_OVERRIDE % (names, name))

_SEQUENCE_TYPES = (types.TupleType, types.ListType, types.StringType)
try: _SEQUENCE_TYPES = _SEQUENCE_TYPES + (types.UnicodeType,)
except AttributeError: pass

# FIXME: this is not complete. errors will be caught only sometimes,
#        depending on the order the functions/methods are processed
#        in the dict.  Need to be able to run through all functions
#        twice, but because the code sucks, this is not possible.
def _checkReturnValueUse(code, func):
    if func.returnValues is None:
        return

    err = None
    opInfo = code.nextOpInfo()
    if func.returnsNoValue():
        # make sure we really know how to check for all the return types
        for rv in func.returnValues:
            if rv[1].type in _UNCHECKABLE_STACK_TYPES:
                return

        if not OP.POP_TOP(opInfo[0]):
            err = msgs.USING_NONE_RETURN_VALUE % utils.safestr(func)
    elif OP.UNPACK_SEQUENCE(opInfo[0]):
        # verify unpacking into proper # of vars
        varCount = opInfo[1]
        stackRV = func.returnValues[0][1]
        returnType = stackRV.getType({})
        funcCount = stackRV.length
        if returnType in _SEQUENCE_TYPES:
            if varCount != funcCount and funcCount > 0:
                err = msgs.WRONG_UNPACK_FUNCTION % (utils.safestr(func), funcCount, varCount)
        elif returnType not in _UNCHECKABLE_STACK_TYPES:
            err = msgs.UNPACK_NON_SEQUENCE % (utils.safestr(func), _getTypeStr(returnType))
    if err:
        code.addWarning(err)

def _handleFunctionCall(codeSource, code, argCount, indexOffset = 0,
                        check_arg_count = 1) :
    'Checks for warnings, returns function called (may be None)'

    if not code.stack :
        return

    kwArgCount = argCount >> utils.VAR_ARGS_BITS
    argCount = argCount & utils.MAX_ARGS_MASK

    # function call on stack is before the args, and keyword args
    funcIndex = argCount + 2 * kwArgCount + 1 + indexOffset
    if funcIndex > len(code.stack) :
        funcIndex = 0
    # to find on stack, we have to look backwards from top of stack (end)
    funcIndex = -funcIndex

    # store the keyword names/keys to check if using named arguments
    kwArgs = []
    if kwArgCount > 0 :
        # loop backwards by 2 (keyword, value) in stack to find keyword args
        for i in range(-2 - indexOffset, (-2 * kwArgCount - 1), -2) :
            kwArgs.append(code.stack[i].data)
        kwArgs.reverse()

    loadValue = code.stack[funcIndex]
    funcName = loadValue.getName()
    returnValue = Stack.makeFuncReturnValue(loadValue, argCount)

    if loadValue.isMethodCall(codeSource.classObject, cfg().methodArgName):
        methodName = loadValue.data[1]
        try :
            m = codeSource.classObject.methods[methodName]
            if m != None :
                objRef = not m.isStaticMethod()
                _checkFunctionArgs(code, m, objRef, argCount, kwArgs,
                                   check_arg_count)
        except KeyError :
            sattr = codeSource.classObject.statics.get(methodName)
            if sattr is not None :
                funcName = sattr.getName()

            if sattr is None and cfg().callingAttribute :
                code.addWarning(msgs.INVALID_METHOD % methodName)

    elif loadValue.type in (Stack.TYPE_ATTRIBUTE, Stack.TYPE_GLOBAL) and \
         type(loadValue.data) in (types.StringType, types.TupleType) :
        # apply(func, (args)), can't check # of args, so just return func
        if loadValue.data == 'apply' :
            loadValue = code.stack[funcIndex+1]
            funcName = loadValue.getName()
        else :
            if cfg().modifyDefaultValue and \
               type(loadValue.data) == types.TupleType :
                _checkModifyDefaultArg(code, loadValue.data[0],
                                       loadValue.data[1])

            func, refClass, method = _getFunction(codeSource.module, loadValue)
            if func == None and type(loadValue.data) == types.TupleType and \
               len(loadValue.data) == 2 :
                # looks like we are making a method call
                data = loadValue.data
                if type(data[0]) == types.StringType :
                    # do we know the type of the local variable?
                    varType = code.typeMap.get(data[0])
                    if varType is not None and len(varType) == 1 :
                        if hasattr(varType[0], 'methods') :
                            # it's a class & we know the type, get the method
                            func = varType[0].methods.get(data[1])
                            if func is not None :
                                method = 1

            if cfg().abstractClasses and refClass and method:
                _checkAbstract(refClass, code, funcName)

            if cfg().stringFind:
                _checkStringFind(code, loadValue)

            if func != None :
                if refClass and func.isClassMethod():
                    argCount = argCount + 1
                _checkFunctionArgs(code, func, method, argCount, kwArgs,
                                   check_arg_count)
                # if this isn't a c'tor, we should check
                if not (refClass and method) and cfg().checkReturnValues:
                    _checkReturnValueUse(code, func)

                if refClass :
                    if method :
                        # c'tor, return the class as the type
                        returnValue = Stack.Item(loadValue, refClass)
                    elif func.isClassMethod():
                        # FIXME: do anything here?
                        pass
                    elif argCount > 0 and cfg().methodArgName and \
                         not func.isStaticMethod() and \
                         code.stack[funcIndex].type == Stack.TYPE_ATTRIBUTE and \
                         code.stack[funcIndex+1].data != cfg().methodArgName:
                        e = msgs.SELF_NOT_FIRST_ARG % (cfg().methodArgName, '')
                        code.addWarning(e)
            elif refClass and method :
                returnValue = Stack.Item(loadValue, refClass)
                if (argCount > 0 or len(kwArgs) > 0) and \
                   not refClass.ignoreAttrs and \
                   not refClass.methods.has_key(utils.INIT) and \
                   not _isexception(refClass.classObject) :
                    code.addWarning(msgs.NO_CTOR_ARGS)
            else :
                returnValue = _checkBuiltin(code, loadValue, argCount, kwArgs,
                                            check_arg_count)
                if returnValue.type is types.NoneType and \
                   not OP.POP_TOP(code.nextOpInfo()[0]) :
                    name = utils.safestr(loadValue.data)
                    if type(loadValue.data) == types.TupleType :
                        name = string.join(loadValue.data, '.')
                    # lambda with setattr is a common way of setting
                    # attributes, so allow it
                    if name != 'setattr' \
                        or code.func.function.func_name != '<lambda>':
                        code.addWarning(msgs.USING_NONE_RETURN_VALUE % name)

    code.stack = code.stack[:funcIndex] + [ returnValue ]
    code.functionsCalled[funcName] = loadValue


def _classHasAttribute(c, attr) :
    return (c.methods.has_key(attr) or c.members.has_key(attr) or
            hasattr(c.classObject, attr))

def _checkClassAttribute(attr, c, code) :
    if _classHasAttribute(c, attr) :
        try :
            del c.memberRefs[attr]
        except KeyError :
            pass
    elif cfg().classAttrExists :
        if attr not in cfg().missingAttrs:
            code.addWarning(msgs.INVALID_CLASS_ATTR % attr)

def _checkModuleAttribute(attr, module, code, ref) :
    try:
        if attr not in module.modules[ref].attributes and \
           not utils.endswith(ref, '.' + attr) :
            code.addWarning(msgs.INVALID_MODULE_ATTR % attr)
    except (KeyError, TypeError):
        # if ref isn't found, or ref isn't even hashable, we don't care
        # we may not know, or ref could be something funky [e for e].method()
        pass

    try:
        _checkClassAttribute(attr, module.classes[ref], code)
    except (KeyError, TypeError):
        # if ref isn't found, or ref isn't even hashable, we don't care
        # we may not know, or ref could be something funky [e for e].method()
        pass


def _getGlobalName(name, func) :
    # get the right name of global refs (for from XXX import YYY)
    opModule = func.function.func_globals.get(name)
    try :
        if opModule and isinstance(opModule, types.ModuleType) :
            name = opModule.__name__
    except :
        # we have to do this in case the class raises an access exception
        # due to overriding __special__() methods
        pass

    return name


def _checkNoEffect(code, ignoreStmtWithNoEffect=0):
    if (not ignoreStmtWithNoEffect and
        OP.POP_TOP(code.nextOpInfo()[0]) and cfg().noEffect):
        code.addWarning(msgs.POSSIBLE_STMT_WITH_NO_EFFECT)
    
def _makeConstant(code, index, factoryFunction) :
    """
    Build a constant on the stack ((), [], or {})

    @param index:           how many items the constant will consume from the
                            stack
    @param factoryFunction: the factory function from L{pychecker.Stack} to
                            use when creating the actual constant
    """
    if index > 0 :
        # replace the bottom of the stack with the result of applying the
        # factory function to it
        code.stack[-index:] = [ factoryFunction(code.stack[-index:]) ]
        _checkNoEffect(code)
    else :
        code.pushStack(factoryFunction())


def _hasGlobal(operand, module, func, main) :
    # returns whether we have a global with the operand's name, because of:
    # - being in the function's global list
    # - main being set to 1
    # - being in the module's list of global operands
    # - being a builtin
    return (func.function.func_globals.has_key(operand) or
             main or module.moduleLineNums.has_key(operand) or
             __builtins__.has_key(operand))

def _checkGlobal(operand, module, func, code, err, main = 0) :
    # if the given operand is not in the global namespace, add the given err
    if not _hasGlobal(operand, module, func, main) :
        code.addWarning(err % operand)
        if not cfg().reportAllGlobals :
            func.function.func_globals[operand] = operand


def _handleComparison(stack, operand) :
    num_ops = 2
    if operand == 'exception match':
        num_ops = 1

    si = min(len(stack), num_ops)
    compareValues = stack[-si:]
    for _ in range(si, 2) :
        compareValues.append(Stack.Item(None, None))
    stack[-si:] = [ Stack.makeComparison(compareValues, operand) ]
    return compareValues

# FIXME: this code needs to be vetted; star imports should actually
# import all the names from the module and put them in the new module
# namespace so we detect collisions
def _handleImport(code, operand, module, main, fromName):
    """
    @param code:     the code block in which the import is happening
    @type  code:     L{Code}
    @param operand:  what is being imported (the module name in case of
                     normal import, or the object names in the module in
                     case of from ... import names/*)
    @type  operand:  str
    @param module:   the module in which the import is happening
    @type  module:   L{pychecker.checker.PyCheckerModule}
    @param main:     whether the import is in the source's global
                     namespace (__main__)
    @type  main:     int (treated as bool)
    @param fromName: the name that's being imported
    @type  fromName: str
    """
    assert type(operand) is str

    # FIXME: this function should be refactored/cleaned up
    key = operand
    tmpOperand = tmpFromName = operand
    if fromName is not None :
        tmpOperand = tmpFromName = fromName
        key = (fromName, operand)

    if cfg().deprecated:
        try:
            undeprecated = python.DEPRECATED_MODULES[tmpFromName]
        except KeyError:
            pass
        else:
            msg = msgs.USING_DEPRECATED_MODULE % tmpFromName
            if undeprecated:
                msg.data = msg.data + msgs.USE_INSTEAD % undeprecated
            code.addWarning(msg)

    if cfg().reimportSelf and tmpOperand == module.module.__name__ :
        code.addWarning(msgs.IMPORT_SELF % tmpOperand)

    modline1 = module.moduleLineNums.get(tmpOperand, None)
    modline2 = module.moduleLineNums.get((tmpFromName, '*'), None)
    key2 = (tmpFromName,)
    if fromName is not None and operand != '*' :
        key2 = (tmpFromName, operand)
    modline3 = module.moduleLineNums.get(key2, None)

    if modline1 is not None or modline2 is not None or modline3 is not None :
        err = None

        if fromName is None :
            if modline1 is not None :
                err = msgs.MODULE_IMPORTED_AGAIN % operand
            elif cfg().mixImport :
                err = msgs.MIX_IMPORT_AND_FROM_IMPORT % tmpFromName
        else :
            if modline3 is not None and operand != '*' :
                err = 'from %s import %s' % (tmpFromName, operand)
                err = msgs.MODULE_MEMBER_IMPORTED_AGAIN % err
            elif modline1 is not None :
                if cfg().mixImport and code.getLineNum() != modline1[1] :
                    err = msgs.MIX_IMPORT_AND_FROM_IMPORT % tmpFromName
            else :
                err = msgs.MODULE_MEMBER_ALSO_STAR_IMPORTED % fromName

        # filter out warnings when files are different (ie, from X import ...)
        if err is not None and cfg().moduleImportErrors :
            codeBytes = module.mainCode
            if codeBytes is None or \
               codeBytes.function.func_code.co_filename == code.func_code.co_filename :
                code.addWarning(err)

    if main :
        fileline = (code.func_code.co_filename, code.getLineNum())
        module.moduleLineNums[key] = fileline
        if fromName is not None :
            module.moduleLineNums[(fromName,)] = fileline


def _handleImportFrom(code, operand, module, main):
    """
    @type  code:    L{Code}
    @param operand: what is being imported; can be * for star imports

    @param main:    whether the import is in the source's global
                    namespace (__main__)
    @type  main:    int (treated as bool)
    """
    # previous opcode is IMPORT_NAME
    fromName = code.stack[-1].data
    if utils.pythonVersion() < utils.PYTHON_2_0 and \
       OP.POP_TOP(code.nextOpInfo()[0]):
        code.popNextOp()
    # FIXME: thomas: why are we pushing the operand, which represents what
    # we import, not where we import from ?
    code.pushStack(Stack.Item(operand, types.ModuleType))
    _handleImport(code, operand, module, main, fromName)


# http://www.python.org/doc/current/lib/typesseq-strings.html
_FORMAT_CONVERTERS = 'diouxXeEfFgGcrs'
# NOTE: lLh are legal in the flags, but are ignored by python, we warn
_FORMAT_FLAGS = '*#- +.' + string.digits

def _getFormatInfo(formatString, code) :
    variables = []

    # first get rid of all the instances of %% in the string, they don't count
    formatString = string.replace(formatString, "%%", "")
    sections = string.split(formatString, '%')
    percentFormatCount = formatCount = string.count(formatString, '%')
    mappingFormatCount = 0

    # skip the first item in the list, it's always empty
    for section in sections[1:] :
        orig_section = section
        if not section:
            w = msgs.INVALID_FORMAT % orig_section
            w.data = w.data + ' (end of format string)'
            code.addWarning(w)
            continue

        # handle dictionary formats
        if section[0] == '(' :
            mappingFormatCount = mappingFormatCount + 1
            varname = string.split(section, ')')
            if varname[1] == '' :
                code.addWarning(msgs.INVALID_FORMAT % section)
            variables.append(varname[0][1:])
            section = varname[1]

        if not section :
            # no format data to check
            continue

        # FIXME: we ought to just define a regular expression to check
        # formatRE = '[ #+-]*([0-9]*|*)(|.(|*|[0-9]*)[diouxXeEfFgGcrs].*'
        stars = 0
        for i in range(0, len(section)) :
            if section[i] in _FORMAT_CONVERTERS :
                break
            if section[i] in _FORMAT_FLAGS :
                if section[i] == '*' :
                    stars = stars + 1
                    if mappingFormatCount > 0 :
                        code.addWarning(msgs.USING_STAR_IN_FORMAT_MAPPING % section)

        if stars > 2 :
            code.addWarning(msgs.TOO_MANY_STARS_IN_FORMAT)

        formatCount = formatCount + stars
        if section[i] not in _FORMAT_CONVERTERS :
            code.addWarning(msgs.INVALID_FORMAT % orig_section)

    if mappingFormatCount > 0 and mappingFormatCount != percentFormatCount :
        code.addWarning(msgs.CANT_MIX_MAPPING_IN_FORMATS)

    return formatCount, variables

def _getConstant(code, module, data) :
    data = utils.safestr(data.data)
    formatString = code.constants.get(data)
    if formatString is not None :
        return formatString

    formatString = module.variables.get(data)
    if formatString is not None and formatString.value is not None :
        return formatString.value
    return None

_UNCHECKABLE_FORMAT_STACK_TYPES = \
      (Stack.TYPE_UNKNOWN, Stack.TYPE_FUNC_RETURN, Stack.TYPE_ATTRIBUTE,
       Stack.TYPE_GLOBAL, Stack.TYPE_EXCEPT)
_UNCHECKABLE_STACK_TYPES = _UNCHECKABLE_FORMAT_STACK_TYPES + (types.NoneType,)

def _getFormatString(code, codeSource) :
    if len(code.stack) <= 1 :
        return ''

    formatString = code.stack[-2]
    if formatString.type != types.StringType or not formatString.const :
        formatString = _getConstant(code, codeSource.module, formatString)
        if formatString is None or type(formatString) != types.StringType :
            return ''
        return formatString
    return formatString.data

    
def _getFormatWarnings(code, codeSource) :
    formatString = _getFormatString(code, codeSource)
    if not formatString :
        return

    args = 0
    count, variables = _getFormatInfo(formatString, code)
    topOfStack = code.stack[-1]
    if topOfStack.isLocals() :
        for varname in variables :
            if not code.unusedLocals.has_key(varname) :
                code.addWarning(msgs.NO_LOCAL_VAR % varname)
            else :
                code.unusedLocals[varname] = None
    else :
        stackItemType = topOfStack.getType(code.typeMap)
        if ((stackItemType == types.DictType and len(variables) > 0) or
            codeSource.func.isParam(topOfStack.data) or
            stackItemType in _UNCHECKABLE_FORMAT_STACK_TYPES) :
            return

        if topOfStack.type == types.TupleType :
            args = topOfStack.length
        elif stackItemType == types.TupleType :
            args = len(code.constants.get(topOfStack.data, (0,)))
        else :
            args = 1

    if args and count != args :
        code.addWarning(msgs.INVALID_FORMAT_COUNT % (count, args))

def _checkAttributeType(code, stackValue, attr) :
    """
    @type code:       {Code}
    @type stackValue: {Stack.Item}
    @type attr:       str
    """

    if not cfg().checkObjectAttrs:
        return

    varTypes = code.typeMap.get(utils.safestr(stackValue.data), None)
    if not varTypes:
        return

    # the value may have been converted on stack (`v`)
    otherTypes = []
    if stackValue.type not in varTypes:
        otherTypes = [stackValue.type]

    for varType in varTypes + otherTypes:
        # ignore built-in types that have no attributes
        if python.METHODLESS_OBJECTS.has_key(varType):
            continue

        attrs = python.BUILTIN_ATTRS.get(varType, None)
        if attrs is not None:
            if attr in attrs:
                return
            continue

        if hasattr(varType, 'ignoreAttrs') :
            if varType.ignoreAttrs or _classHasAttribute(varType, attr) :
                return
        elif not hasattr(varType, 'attributes') or attr in varType.attributes :
            return

    code.addWarning(msgs.OBJECT_HAS_NO_ATTR % (stackValue.data, attr))


def _getTypeStr(t):
    returnStr = utils.safestr(t)
    strs = string.split(returnStr, "'")
    try:
        if len(strs) == 3:
            returnStr = strs[-2]
    except IndexError:
        pass
    return returnStr


def _getLineNum(co, instr_index):
    co_lnotab = co.co_lnotab
    lineno = co.co_firstlineno
    addr = 0
    for lnotab_index in range(0, len(co_lnotab), 2):
        addr = addr + ord(co_lnotab[lnotab_index])
        if addr > instr_index:
            return lineno
        lineno = lineno + ord(co_lnotab[lnotab_index+1])
    return lineno


class Code :
    """
    Hold all the code state information necessary to find warnings.

    @ivar bytes:        the raw bytecode for this code object
    @type bytes:        str
    @ivar func_code:    the function code object
    @type func_code:    L{types.CodeType}
    @ivar index:        index into bytes for the current instruction
    @type index:        int
    @ivar extended_arg: extended argument for the current instruction
    @type extended_arg: int
    @ivar maxCode:      length of bytes
    @type maxCode:      int
    @ivar stack:        
    @type stack:        list of L{Stack.Item}
    @ivar warnings:     list of warnings
    @type warnings:     list of L{pychecker.Warning.Warning}
    @ivar returnValues: tuple of (line number, stack item,
                                  index to next instruction)
    @type returnValues: tuple of (int, L{Stack.Item}, int)
    @ivar typeMap:      dict of token name -> list of wrapped types;
                        type can also be string defined in L{Stack}
                        with TYPE_
    @type typeMap:      dict of str -> list of str or L{pcmodules.Class}
    @ivar codeObjects:  dict of name/anonymous index -> code
    @type codeObjects:  dict of str/int -> L{types.CodeType}
    @ivar codeOrder:    ordered list of when the given key was added to
                        codeObjects
    @type codeOrder:    list of str/int
    """

    # opcodes are either 1 byte (no argument) or 3 bytes (with argument) long
    # opcode can be EXTENDED_ARGS which then accumulates to the previous arg
    # to span values > 64K
    def __init__(self) :
        self.bytes = None
        self.func = None
        self.func_code = None
        self.index = 0
        self.indexList = []
        self.extended_arg = 0
        self.lastLineNum = 0
        self.maxCode = 0
        self.has_except = 0
        self.try_finally_first = 0
        self.starts_and_ends_with_finally = 0

        self.returnValues = []
        self.raiseValues = []
        self.stack = []

        self.unpackCount = 0
        self.loops = 0
        self.branches = {}

        self.warnings = []

        self.globalRefs = {}
        self.unusedLocals = {}
        self.deletedLocals = {}
        self.functionsCalled = {}
        self.typeMap = {}
        self.constants = {}
        self.codeObjects = {}
        self.codeOrder = []

    def init(self, func) :
        self.func = func
        self.func_code, self.bytes, self.index, self.maxCode, self.extended_arg = \
                        OP.initFuncCode(func.function)
        self.lastLineNum = self.func_code.co_firstlineno
        self.returnValues = []

        # initialize the arguments to unused
        for arg in func.arguments() :
            self.unusedLocals[arg] = 0
            self.typeMap[arg] = [ Stack.TYPE_UNKNOWN ]

    def getLineNum(self):
        line = self.lastLineNum
        # if we don't have linenum info, calc it from co_lntab & index
        if line == self.func_code.co_firstlineno:
            # FIXME: this could be optimized, if we kept last line info
            line = _getLineNum(self.func_code, self.index - 1)
        return line

    def getWarning(self, err, line = None) :
        """
        @type err:  L{msgs.WarningClass}
        """
        if line is None :
            line = self.getLineNum()
        return Warning.Warning(self.func_code, line, err)

    def addWarning(self, err, line = None) :
        """
        @type line: int or L{types.CodeType} or None
        @type err:  L{Warning.Warning} or L{msgs.WarningClass}
        """
        w = err
        if not isinstance(w, Warning.Warning):
            w = self.getWarning(err, line)
        utils.debug('adding warning: %s', w.format())
        self.warnings.append(w)

    def popNextOp(self) :
        """
        Pops the next bytecode instruction from the code object for processing.

        The opcode and oparg are integers coming from the byte code.

        The operand is the object referenced by the oparg, from the
        respective array (co_consts, co_names, co_varnames)

        Changes L{index} and L{extended_arg} to point to the next operation.

        @returns: tuple of (opcode, oparg, operand)
        @rtype:   tuple of (int, int, object)
        """
        self.indexList.append(self.index)
        info = OP.getInfo(self.bytes, self.index, self.extended_arg)
        op, oparg, self.index, self.extended_arg = info
        if op < OP.HAVE_ARGUMENT :
            utils.debug("DIS  %d %s" % (self.indexList[-1], OP.name[op]))
            operand = None
        else :
            operand = OP.getOperand(op, self.func_code, oparg)
            self.label = label = OP.getLabel(op, oparg, self.index)
            utils.debug("DIS  %d %s" % (self.indexList[-1], OP.name[op]), oparg, operand)
            if label != None :
                self.addBranch(label)

        return op, oparg, operand

    def nextOpInfo(self, offset = 0) :
        """
        Peeks ahead at the next instruction.

        @returns: tuple of (opcode, oparg, index) or (-1, 0, -1) if no next
        @rtype:   tuple of (int, int, int)
        """
        try :
            return OP.getInfo(self.bytes, self.index + offset, 0)[0:3]
        except IndexError :
            return -1, 0, -1

    def getFirstOp(self) :
        # find the first real op, maybe we should not check if params are used
        i = extended_arg = 0
        while i < self.maxCode :
            op, oparg, i, extended_arg = OP.getInfo(self.bytes, i, extended_arg)
            if not OP.LINE_NUM(op) :
                if not (OP.LOAD_CONST(op) or OP.LOAD_GLOBAL(op)) :
                    return op
        raise RuntimeError('Could not find first opcode in function')

    def pushStack(self, item, ignoreStmtWithNoEffect=0):
        self.stack.append(item)
        _checkNoEffect(self, ignoreStmtWithNoEffect)

    def popStack(self) :
        if self.stack :
            del self.stack[-1]

    def popStackItems(self, count) :
        stackLen = len(self.stack)
        if stackLen > 0 :
            count = min(count, stackLen)
            del self.stack[-count:]

    def unpack(self) :
        if self.unpackCount :
            self.unpackCount = self.unpackCount - 1
        else :
            self.popStack()

    def __getStringStackType(self, data) :
        try :
            return data.getType({})
        except AttributeError :
            return Stack.TYPE_UNKNOWN

    def __getStackType(self) :
        if not self.stack :
            return Stack.TYPE_UNKNOWN

        if not self.unpackCount :
            return self.__getStringStackType(self.stack[-1])

        data = self.stack[-1].data
        if type(data) == types.TupleType :
            try :
                return self.__getStringStackType(data[len(data)-self.unpackCount])
            except IndexError :
                # happens when unpacking a var for which we don't know the size
                pass

        return Stack.TYPE_UNKNOWN

    def setType(self, name) :
        valueList = self.typeMap.get(name, [])
        newType = self.__getStackType()
        # longs are being merged with ints, assume they are the same
        # comparisons are really ints anyways
        if newType in (types.LongType, Stack.TYPE_COMPARISON):
            newType = types.IntType
        if newType not in valueList :
            valueList.append(newType)

            # need to ignore various types (Unknown, Func return values, etc)
            # also ignore None, don't care if they use it and a real type
            if valueList and newType not in _UNCHECKABLE_STACK_TYPES and \
               cfg().inconsistentTypes:
                oldTypes = []
                # only add types to the value list that are "interesting"
                for typeToAdd in valueList:
                    if typeToAdd not in _UNCHECKABLE_STACK_TYPES and \
                       typeToAdd != newType:
                        oldTypes.append(_getTypeStr(typeToAdd))
                # do we have any "interesting" old types?  if so, warn
                if oldTypes:
                    self.addWarning(msgs.INCONSISTENT_TYPE % \
                                    (name, oldTypes, _getTypeStr(newType)))
        self.typeMap[name] = valueList

    def addReturn(self) :
        if len(self.stack) > 0 :
            value = (self.getLineNum(), self.stack[-1], self.nextOpInfo()[2])
            self.returnValues.append(value)
            self.popStack()

    def addRaise(self) :
        self.raiseValues.append((self.getLineNum(), None, self.nextOpInfo()[2]))

    def addBranch(self, label) :
        if label is not None :
            self.branches[label] = self.branches.get(label, 0) + 1

    def removeBranch(self, label) :
        branch = self.branches.get(label, None)
        if branch is not None :
            if branch == 1 :
                del self.branches[label]
            else :
                self.branches[label] = branch - 1

    def remove_unreachable_code(self, label) :
        if len(self.indexList) >= 2 :
            index = self.indexList[-2]
            if index >= 0 and OP.POP_BLOCK(ord(self.bytes[index])) :
                index = self.indexList[-3]
            if index >= 0 :
                op = ord(self.bytes[index])
                if OP.RETURN_VALUE(op) or OP.RAISE_VARARGS(op) or \
                   OP.END_FINALLY(ord(self.bytes[label-1])) :
                    self.removeBranch(label)

    def updateCheckerArgs(self, operand) :
        """
        If the operand is a __pychecker__ argument string,
        update the checker arguments for this Code object.

        @rtype:   bool
        @returns: whether the checker arguments were updated.
        """
        rc = utils.shouldUpdateArgs(operand)
        if rc :
            # pass the location of the __pychecker__ arguments
            utils.updateCheckerArgs(self.stack[-1].data, self.func_code,
                                    self.getLineNum(), self.warnings)
        return rc
        
    def updateModuleLineNums(self, module, operand) :
        """
        @type module:  L{pychecker.checker.PyCheckerModule}
        """
        filelist = (self.func_code.co_filename, self.getLineNum())
        module.moduleLineNums[operand] = filelist

    def addCodeObject(self, key, code):
        """
        Add the given code object, maintaining order of addition.

        @param key:  the key to be used for storing in self.codeObjects
        @type  key:  str or int
        @param code: the code to be stored
        @type  code: L{types.CodeType}
        """
        self.codeObjects[key] = code
        self.codeOrder.append(key)

class CodeSource:
    """
    Holds source information about a code block (module, class, func, etc)

    @ivar module:       module the source is for
    @type module:       L{pychecker.checker.PyCheckerModule}
    @ivar func:         function the source is for
    @type func:         L{pychecker.function.Function}
    @ivar classObject:  the class object, if applicable
    @type classObject:  L{pychecker.checker.Class} or None
    @ivar main:         whether this code block is in the source's global
                        namespace (__main__)
    @type main:         int (used as bool)
    @ivar in_class:     whether this code block is inside a class scope
    @type in_class:     int (used as bool)
    @ivar calling_code: list of functions that call this source
    @type calling_code: list of callable
    
    """
    def __init__(self, module, func, c, main, in_class, code):
        self.module = module
        self.func = func
        self.classObject = c
        self.main = main
        self.in_class = in_class
        self.code = code
        self.calling_code = []

def _checkException(code, name) :
    if code.stack and code.stack[-1].type == Stack.TYPE_EXCEPT :
        if __builtins__.has_key(name) :
            code.addWarning(msgs.SET_EXCEPT_TO_BUILTIN % name)

def _checkAssign(code, name):
    if name in _BAD_ASSIGN_NAMES:
        code.addWarning(msgs.SHOULDNT_ASSIGN_BUILTIN % name)
    else:
        cap = string.capitalize(name)
        if cap in _BAD_ASSIGN_NAMES:
            code.addWarning(msgs.SHOULDNT_ASSIGN_NAME % (name, cap))

def _checkVariableOperationOnItself(code, lname, msg):
    if code.stack and code.stack[-1].getName() == lname:
        code.addWarning(msg % lname)

# checks if the given varname is a known future keyword, and warn if so
def _checkFutureKeywords(code, varname) :
    kw = python.FUTURE_KEYWORDS.get(varname)
    if kw is not None :
        code.addWarning(msgs.USING_KEYWORD % (varname, kw))

### dispatcher functions for operands

# All these functions have the following documentation:
# @type  oparg:      int
# @param oparg:
# @type  operand:    object
# @param operand:
# @param codeSource:
# @type  codeSource: L{CodeSource}
# @param code:
# @type  code:       L{Code}

# Implements name = TOS. namei is the index of name in the attribute co_names
# of the code object. The compiler tries to use STORE_FAST or STORE_GLOBAL if
# possible.
def _STORE_NAME(oparg, operand, codeSource, code) :
    if not code.updateCheckerArgs(operand) :
        module = codeSource.module

        # not a __pychecker__ operand, so continue checking
        _checkFutureKeywords(code, operand)

        if not codeSource.in_class :
            _checkShadowBuiltin(code, operand)

            # complain if the code is called and declares global on an
            # undefined name
            if not codeSource.calling_code :
                _checkGlobal(operand, module, codeSource.func, code,
                             msgs.GLOBAL_DEFINED_NOT_DECLARED, codeSource.main)
        else :
            # we're in a class

            if code.stack :
                codeSource.classObject.statics[operand] = code.stack[-1]
                codeSource.classObject.lineNums[operand] = code.getLineNum()

        var = module.variables.get(operand)
        if var is not None and code.stack and code.stack[-1].const :
            var.value = code.stack[-1].data

        if code.unpackCount :
            code.unpackCount = code.unpackCount - 1
        else:
            _checkAssign(code, operand)
            _checkException(code, operand)
            code.popStack()
        if not module.moduleLineNums.has_key(operand) and codeSource.main :
            code.updateModuleLineNums(module, operand)

_STORE_GLOBAL = _STORE_NAME

def _checkLoadGlobal(codeSource, code, varname) :
    _checkFutureKeywords(code, varname)
    should_check = 1
    if code.func_code.co_name == utils.LAMBDA :
        # this could really be a local reference, check first
        if not codeSource.main and codeSource.calling_code:
            func = getattr(codeSource.calling_code[-1], 'function', None)
            if func is not None and varname in func.func_code.co_varnames :
                _handleLoadLocal(code, codeSource, varname)
                should_check = 0

    if should_check :
        # if a global var starts w/__ and the global is referenced in a class
        # we have to strip off the _class-name, to get the original name
        if codeSource.classObject and \
           utils.startswith(varname, '_' + codeSource.classObject.name + '__'):
            varname = varname[len(codeSource.classObject.name)+1:]
            
        # make sure we remember each global ref to check for unused
        code.globalRefs[_getGlobalName(varname, codeSource.func)] = varname
        if not codeSource.in_class :
            _checkGlobal(varname, codeSource.module, codeSource.func,
                         code, msgs.INVALID_GLOBAL)

def _LOAD_NAME(oparg, operand, codeSource, code) :
    _checkLoadGlobal(codeSource, code, operand)

    # if there was from XXX import *, _* names aren't imported
    if codeSource.module.modules.has_key(operand) and \
       hasattr(codeSource.module.module, operand) :
        operand = getattr(codeSource.module.module, operand).__name__

    opType, const = Stack.TYPE_GLOBAL, 0
    if operand == 'None' :
        opType, const = types.NoneType, 0
    elif operand == 'Ellipsis' :
        opType, const = types.EllipsisType, 1
    code.pushStack(Stack.Item(operand, opType, const))

_LOAD_GLOBAL = _LOAD_NAME

def _LOAD_DEREF(oparg, operand, codeSource, code) :
    if type(oparg) == types.IntType :
        func_code = code.func_code
        try:
            argname = func_code.co_cellvars[oparg]
        except IndexError:
            argname = func_code.co_freevars[oparg - len(func_code.co_cellvars)]
        code.pushStack(Stack.Item(argname, types.StringType))
        if code.func_code.co_name != utils.LAMBDA :
            code.unusedLocals[argname] = None
    else :
        _LOAD_GLOBAL(oparg, operand, codeSource, code)

_LOAD_CLOSURE = _LOAD_DEREF

# Implements del name, where namei is the index into co_names attribute of the
# code object.
def _DELETE_NAME(oparg, operand, codeSource, code) :
    _checkLoadGlobal(codeSource, code, operand)
    # FIXME: handle deleting global multiple times
_DELETE_GLOBAL = _DELETE_NAME

def _make_const(value):
    if type(value) == types.TupleType:
        return Stack.makeTuple(map(_make_const, value))
    return Stack.Item(value, type(value), 1)

def _LOAD_CONST(oparg, operand, codeSource, code):
    code.pushStack(_make_const(operand))

    # add code objects to code.codeObjects
    if type(operand) == types.CodeType:
        name = operand.co_name
        obj = code.codeObjects.get(name, None)
        if name in (utils.LAMBDA, utils.GENEXP, utils.GENEXP25):
            # use a unique key, so we can have multiple lambdas
            if code.index in code.codeObjects:
                msg = "LOAD_CONST: code.index %d is already in codeObjects" \
                    % code.index
                code.addWarning(msgs.CHECKER_BROKEN % msg)
            code.addCodeObject(code.index, operand)
        elif obj is None:
            code.addCodeObject(name, operand)
        elif cfg().redefiningFunction:
            code.addWarning(msgs.REDEFINING_ATTR % (name, obj.co_firstlineno))


def _checkLocalShadow(code, module, varname) :
    # FIXME: why is this only for variables, not for classes/functions ?
    if module.variables.has_key(varname) and cfg().shadows :
        line = module.moduleLineNums.get(varname, ('<unknown>', 0))
        w = code.getWarning(msgs.LOCAL_SHADOWS_GLOBAL % (varname, line[1]))
        if line[0] != w.file:
            w.err = '%s in file %s' % (w.err, line[0])
        code.addWarning(w)

def _checkShadowBuiltin(code, varname) :
    # Check if the given variable name shadows a builtin
    if __builtins__.has_key(varname) and varname[0] != '_' and \
       cfg().shadowBuiltins:
        code.addWarning(msgs.VARIABLE_SHADOWS_BUILTIN % varname)

def _checkLoadLocal(code, codeSource, varname, deletedWarn, usedBeforeSetWarn) :
    _checkFutureKeywords(code, varname)
    deletedLine = code.deletedLocals.get(varname)
    if deletedLine :
        code.addWarning(deletedWarn % (varname, deletedLine))
    elif not code.unusedLocals.has_key(varname) and \
         not codeSource.func.isParam(varname) :
        code.addWarning(usedBeforeSetWarn % varname)
    code.unusedLocals[varname] = None
    _checkLocalShadow(code, codeSource.module, varname)

def _handleLoadLocal(code, codeSource, varname) :
    _checkLoadLocal(code, codeSource, varname,
                    msgs.LOCAL_DELETED, msgs.VAR_USED_BEFORE_SET)

def _LOAD_FAST(oparg, operand, codeSource, code) :
    code.pushStack(Stack.Item(operand, type(operand)))
    _handleLoadLocal(code, codeSource, operand)

def _STORE_FAST(oparg, operand, codeSource, code) :
    if not code.updateCheckerArgs(operand) :
        # not a __pychecker__ operand, so continue checking
        _checkFutureKeywords(code, operand)
        if code.stack and code.stack[-1].type == types.StringType and \
               not code.stack[-1].const:
            _checkVariableOperationOnItself(code, operand,
                                            msgs.SET_VAR_TO_ITSELF)
        code.setType(operand)
        if not code.unpackCount and code.stack and \
           (code.stack[-1].const or code.stack[-1].type == types.TupleType) :
            if code.constants.has_key(operand) :
                del code.constants[operand]
            else :
                code.constants[operand] = code.stack[-1].data

        _checkLocalShadow(code, codeSource.module, operand)
        _checkShadowBuiltin(code, operand)
        _checkAssign(code, operand)
        _checkException(code, operand)
        if code.deletedLocals.has_key(operand) :
            del code.deletedLocals[operand]
        if not code.unusedLocals.has_key(operand) :
            errLine = code.getLineNum()
            if code.unpackCount and not cfg().unusedLocalTuple :
                errLine = -errLine
            code.unusedLocals[operand] = errLine
        code.unpack()

def _DELETE_FAST(oparg, operand, codeSource, code) :
    _checkLoadLocal(code, codeSource, operand,
                    msgs.LOCAL_ALREADY_DELETED, msgs.VAR_DELETED_BEFORE_SET)
    code.deletedLocals[operand] = code.getLineNum()

def _checkAttribute(top, operand, codeSource, code) :
    if top.data == cfg().methodArgName and codeSource.classObject != None :
        _checkClassAttribute(operand, codeSource.classObject, code)
    elif type(top.type) == types.StringType or top.type == types.ModuleType :
        _checkModuleAttribute(operand, codeSource.module, code, top.data)
    else :
        _checkAttributeType(code, top, operand)

def _checkExcessiveReferences(code, top, extraAttr = None) :
    if cfg().maxReferences <= 0 :
        return

    try :
        data = top.data
        if extraAttr is not None :
            data = data + (extraAttr,)
        
        maxReferences = cfg().maxReferences
        if data[0] == cfg().methodArgName:
            maxReferences = maxReferences + 1
        if len(data) > maxReferences :
            name = string.join(top.data, '.')
            code.addWarning(msgs.TOO_MANY_REFERENCES % (maxReferences, name))
    except TypeError :
        pass

def _checkDeprecated(code, identifierTuple):
    # check deprecated module.function
    try:
        name = string.join(identifierTuple, '.')
        undeprecated = python.DEPRECATED_ATTRS[name]
    except (KeyError, TypeError):
        pass
    else:
        msg = msgs.USING_DEPRECATED_ATTR % name
        if undeprecated:
            msg.data = msg.data + msgs.USE_INSTEAD % undeprecated
        code.addWarning(msg)

def _LOAD_ATTR(oparg, operand, codeSource, code) :
    if len(code.stack) > 0 :
        top = code.stack[-1]
        _checkAttribute(top, operand, codeSource, code)
        top.addAttribute(operand)

        if len(top.data) == 2:
            if cfg().deprecated:
                _checkDeprecated(code, top.data)

            try:
                insecure = python.SECURITY_FUNCS.get(top.data[0])
            except TypeError:
                pass
            else:
                if insecure and insecure.has_key(operand):
                    func = string.join(top.data, '.')
                    code.addWarning(msgs.USING_INSECURE_FUNC % func)

        nextOp = code.nextOpInfo()[0]
        if not OP.LOAD_ATTR(nextOp) :
            if OP.POP_TOP(nextOp) and cfg().noEffect:
                code.addWarning(msgs.POSSIBLE_STMT_WITH_NO_EFFECT)
            else :
                _checkExcessiveReferences(code, top)

def _ok_to_set_attr(classObject, basename, attr) :
    return (cfg().onlyCheckInitForMembers and classObject != None and
            basename == cfg().methodArgName and 
            not _classHasAttribute(classObject, attr))

def _STORE_ATTR(oparg, operand, codeSource, code) :
    if code.stack :
        top = code.stack.pop()
        top_name = '%s.%s' % (top.getName(), operand)
        try:
            # FIXME: this is a hack to handle code like:
            #        a.a = [x for x in range(2) if x > 1]
            previous = code.stack[-1]
        except IndexError:
            previous = None
        if top.type in (types.StringType, Stack.TYPE_ATTRIBUTE) and \
           previous and previous.type == Stack.TYPE_ATTRIBUTE:
            _checkVariableOperationOnItself(code, top_name,
                                            msgs.SET_VAR_TO_ITSELF)
        _checkExcessiveReferences(code, top, operand)
        if _ok_to_set_attr(codeSource.classObject, top.data, operand) :
            code.addWarning(msgs.INVALID_SET_CLASS_ATTR % operand)
    code.unpack()

def _DELETE_ATTR(oparg, operand, codeSource, code) :
    if len(code.stack) > 0 :
        _checkAttribute(code.stack[-1], operand, codeSource, code)

def _getExceptionInfo(codeSource, item):
    # FIXME: probably ought to try to handle raise module.Error
    if item.type is types.StringType and item.const == 1:
        return item.data, 1

    e = None
    if item.type is Stack.TYPE_GLOBAL:
        try:
            e = eval(item.data)
        except NameError:
            pass

    if not e:
        try:
            c = codeSource.module.classes.get(item.data)
        except TypeError:     # item.data may not be hashable (e.g., list)
            return e, 0

        if c is not None:
            e = c.classObject
        else:
            v = codeSource.module.variables.get(item.data)
            if v is not None:
                return v, (v.type == types.StringType)
    return e, 0

_UNCHECKABLE_CATCH_TYPES = (Stack.TYPE_UNKNOWN, Stack.TYPE_ATTRIBUTE)
def _checkCatchException(codeSource, code, item):
    if not cfg().badExceptions:
        return

    if item.data is None or item.type in _UNCHECKABLE_CATCH_TYPES:
        return

    e, is_str = _getExceptionInfo(codeSource, item)
    if is_str:
        code.addWarning(msgs.CATCH_STR_EXCEPTION % item.data)
    elif e is not None and not _isexception(e):
        code.addWarning(msgs.CATCH_BAD_EXCEPTION % item.data)

def _handleExceptionChecks(codeSource, code, checks):
    for item in checks:
        if item is not None:
            if item.type is not types.TupleType:
                _checkCatchException(codeSource, code, item)
            else:
                for ti in item.data:
                    if isinstance(ti, Stack.Item):
                        _checkCatchException(codeSource, code, ti)

_BOOL_NAMES = ('True', 'False')
_BAD_ASSIGN_NAMES = _BOOL_NAMES + ('None',)

def _checkBoolean(code, checks):
    for item in checks:
        try:
            data = string.capitalize(item.data)
            if item.type is Stack.TYPE_GLOBAL and data in _BOOL_NAMES:
                code.addWarning(msgs.BOOL_COMPARE % item.data)
        except (AttributeError, TypeError):
            # TypeError is necessary for Python 1.5.2
            pass # ignore items that are not a StackItem or a string

def _COMPARE_OP(oparg, operand, codeSource, code) :
    compareValues = _handleComparison(code.stack, operand)
    if oparg == OP.EXCEPT_COMPARISON:
        _handleExceptionChecks(codeSource, code, compareValues)
    elif oparg < OP.IN_COMPARISON: # '<', '<=', '==', '!=', '>', '>='
        _checkBoolean(code, compareValues)
    elif oparg < OP.IS_COMPARISON: # 'in', 'not in'
        # TODO: any checks that should be done here?
        pass
    elif cfg().isLiteral:
        # X is Y   or   X is not Y   comparison
        second_arg = code.stack[-1].data[2]
        # FIXME: how should booleans be handled, need to think about it
##        if second_arg.const or (second_arg.type == Stack.TYPE_GLOBAL and
##                                second_arg.data in ['True', 'False']):
        if second_arg.const and second_arg.data is not None:
            data = second_arg.data
            if second_arg.type is types.DictType:
                data = {}
            not_str = ''
            if oparg != OP.IS_COMPARISON:
                not_str = ' not'
            code.addWarning(msgs.IS_LITERAL % (not_str, data))

    _checkNoEffect(code)

def _IMPORT_NAME(oparg, operand, codeSource, code) :
    code.pushStack(Stack.Item(operand, types.ModuleType))

    # only handle straight import names; FROM or STAR are done separately
    nextOp = code.nextOpInfo()[0]
    if not OP.IMPORT_FROM(nextOp) and not OP.IMPORT_STAR(nextOp):
        _handleImport(code, operand, codeSource.module, codeSource.main, None)

def _IMPORT_FROM(oparg, operand, codeSource, code) :
    _handleImportFrom(code, operand, codeSource.module, codeSource.main)
    # this is necessary for python 1.5 (see STORE_GLOBAL/NAME)
    if utils.pythonVersion() < utils.PYTHON_2_0 :
        code.popStack()
        if not codeSource.main :
            code.unusedLocals[operand] = None
        elif not codeSource.module.moduleLineNums.has_key(operand) :
            code.updateModuleLineNums(codeSource.module, operand)

# Loads all symbols not starting with '_' directly from the module TOS to the
# local namespace. The module is popped after loading all names. This opcode
# implements from module import *.
def _IMPORT_STAR(oparg, operand, codeSource, code):
    # codeSource: the piece of source code doing the import 
    # code:       the piece of code matching codeSource doing the import
    _handleImportFrom(code, '*', codeSource.module, codeSource.main)

# Python 2.3 introduced some optimizations that create problems
# this is a utility for ignoring these cases
def _shouldIgnoreCodeOptimizations(code, bytecodes, offset, length=None):
    if utils.pythonVersion() < utils.PYTHON_2_3:
        return 0

    if length is None:
        length = offset - 1
    try:
        start = code.index - offset
        return bytecodes == code.bytes[start:start+length]
    except IndexError:
        return 0

# In Python 2.3, a, b = 1,2 generates this code:
# ...
# ROT_TWO
# JUMP_FORWARD 2
# DUP_TOP
# POP_TOP
#
# which generates a Possible stmt w/no effect

# ROT_TWO = 2; JUMP_FORWARD = 110; 2, 0 is the offset (2)
_IGNORE_SEQ = '%c%c%c%c' % (2, 110, 2, 0)
def _shouldIgnoreNoEffectWarning(code):
    return _shouldIgnoreCodeOptimizations(code, _IGNORE_SEQ, 5)

def _DUP_TOP(oparg, operand, codeSource, code) :
    if len(code.stack) > 0 :
        code.pushStack(code.stack[-1], _shouldIgnoreNoEffectWarning(code))

# Duplicate count items, keeping them in the same order. Due to implementation
# limits, count should be between 1 and 5 inclusive.
def _DUP_TOPX(oparg, operand, codeSource, code):
    if oparg > 5:
        code.addWarning(msgs.Warning(
            'DUP_TOPX has oparg %d, should not be more than 5' % oparg))

    if len(code.stack) > oparg - 1:
        source = code.stack[-oparg:]
        for item in source:
            code.pushStack(item, _shouldIgnoreNoEffectWarning(code))

def _popn(code, n) :
    if len(code.stack) >= 2 :
        loadValue = code.stack[-2]
        if cfg().modifyDefaultValue and loadValue.type == types.StringType :
            _checkModifyDefaultArg(code, loadValue.data)

    code.popStackItems(n)
    
def _DELETE_SUBSCR(oparg, operand, codeSource, code) :
    _popn(code, 2)

def _STORE_SUBSCR(oparg, operand, codeSource, code) :
    _popn(code, 3)

def _CALL_FUNCTION(oparg, operand, codeSource, code) :
    _handleFunctionCall(codeSource, code, oparg)

def _CALL_FUNCTION_VAR(oparg, operand, codeSource, code) :
    _handleFunctionCall(codeSource, code, oparg, 1, 0)

def _CALL_FUNCTION_KW(oparg, operand, codeSource, code) :
    _handleFunctionCall(codeSource, code, oparg, 1)

def _CALL_FUNCTION_VAR_KW(oparg, operand, codeSource, code) :
    _handleFunctionCall(codeSource, code, oparg, 2, 0)

# Pushes a new function object on the stack. TOS is the code associated with
# the function. The function object is defined to have argc default parameters,
# which are found below TOS.
def _MAKE_FUNCTION(oparg, operand, codeSource, code) :
    newValue = Stack.makeFuncReturnValue(code.stack[-1], oparg)
    code.popStackItems(oparg+1)
    code.pushStack(newValue)

def _MAKE_CLOSURE(oparg, operand, codeSource, code) :
    _MAKE_FUNCTION(max(0, oparg - 1), operand, codeSource, code)

def _BUILD_MAP(oparg, operand, codeSource, code) :
    # Pushes a new dictionary object onto the stack. The dictionary is
    # pre-sized to hold count entries.
    # before python 2.6, the argument was always zero
    # since 2.6, the argument is the size the dict should be pre-sized to
    # In either case, _BUILD_MAP does not consume anything from the stack
    _makeConstant(code, 0, Stack.makeDict)
def _BUILD_TUPLE(oparg, operand, codeSource, code) :
    # Creates a tuple consuming count items from the stack, and pushes the
    # resulting tuple onto the stack.
    _makeConstant(code, oparg, Stack.makeTuple)
def _BUILD_LIST(oparg, operand, codeSource, code) :
    # Works as BUILD_TUPLE, but creates a list.
    _makeConstant(code, oparg, Stack.makeList)
def _STORE_MAP(oparg, operand, codeSource, code) :
    _popn(code, 2)

# Creates a new class object. TOS is the methods dictionary, TOS1 the tuple
# of the names of the base classes, and TOS2 the class name.
def _BUILD_CLASS(oparg, operand, codeSource, code) :
    newValue = Stack.makeFuncReturnValue(code.stack[-1], types.ClassType)
    code.popStackItems(3)
    code.pushStack(newValue)

# example disassembly:
# ('  18 BUILD_LIST', 6, None)
# ('  21 STORE_FAST', 0, 'l')
# ('  24 LOAD_FAST', 0, 'l')
# ('  27 LOAD_CONST', 7, 0)
# ('  30 LOAD_CONST', 0, None)
# ('  33 LOAD_CONST', 2, 2)
# ('  36 BUILD_SLICE', 3, None)
def _BUILD_SLICE(oparg, operand, codeSource, code):
    argCount = oparg
    assert argCount in [2, 3]

    if argCount == 3:
        start = code.stack[-3].data
        stop = code.stack[-2].data
        step = code.stack[-1].data
        sourceName = code.stack[-4].data
    else:
        start = code.stack[-2].data
        stop = code.stack[-1].data
        step = None
        sourceName = code.stack[-3].data

    if sourceName in code.constants:
        source = code.constants[sourceName]
        if step:
            sl = source[start:stop:step]
        else:
            sl = source[start:stop]
        # push new slice on stack
        code.stack[-argCount:] = [Stack.Item(sl, types.ListType, 1, len(sl)), ]
    else:
        # FIXME: not sure what we do with a non-constant slice ?
        # push a non-constant slice of the source on stack
        code.stack[-argCount:] = [Stack.Item(
            sourceName, types.ListType, 0, 1), ]

    _checkNoEffect(code)

# old pre-2.7 LIST_APPEND, argumentless
def _LIST_APPEND(oparg, operand, codeSource, code):
    code.popStackItems(2)

# new 2.7 LIST_APPEND, takes argument as number of items to append
def _LIST_APPEND_2_7(oparg, operand, codeSource, code):
    count = oparg
    code.popStackItems(1 + count)
  
def _modifyStackName(code, suffix):
    if code.stack:
        tos = code.stack[-1]
        tos_type = type(tos.data)
        if tos_type == types.StringType:
            tos.data = tos.data + suffix
        elif tos_type == types.TupleType and \
             type(tos.data[-1]) == types.StringType:
            tos.data = tos.data[:-1] + (tos.data[-1] + suffix,)

def _UNARY_CONVERT(oparg, operand, codeSource, code) :
    if code.stack:
        stackValue = code.stack[-1]
        if stackValue.data == cfg().methodArgName and \
           stackValue.const == 0 and codeSource.classObject is not None and \
           codeSource.func.function.func_name == '__repr__' :
            code.addWarning(msgs.USING_SELF_IN_REPR)
        stackValue.data = utils.safestr(stackValue.data)
        stackValue.type = types.StringType
    _modifyStackName(code, '-repr')

def _UNARY_POSITIVE(oparg, operand, codeSource, code) :
    if OP.UNARY_POSITIVE(code.nextOpInfo()[0]) :
        code.addWarning(msgs.STMT_WITH_NO_EFFECT % '++')
        code.popNextOp()
    elif cfg().unaryPositive and code.stack and not code.stack[-1].const :
        code.addWarning(msgs.UNARY_POSITIVE_HAS_NO_EFFECT)
    _modifyStackName(code, '-pos')

def _UNARY_NEGATIVE(oparg, operand, codeSource, code) :
    if OP.UNARY_NEGATIVE(code.nextOpInfo()[0]) :
        code.addWarning(msgs.STMT_WITH_NO_EFFECT % '--')
    _modifyStackName(code, '-neg')

def _UNARY_NOT(oparg, operand, codeSource, code) :
    _modifyStackName(code, '-not')

def _UNARY_INVERT(oparg, operand, codeSource, code) :
    if OP.UNARY_INVERT(code.nextOpInfo()[0]) :
        code.addWarning(msgs.STMT_WITH_NO_EFFECT % '~~')
    _modifyStackName(code, '-invert')


def _popStackRef(code, operand, count = 2) :
    # pop count items, then push a ref to the operand on the stack
    code.popStackItems(count)
    code.pushStack(Stack.Item(operand, Stack.TYPE_UNKNOWN))

def _popModifiedStack(code, suffix=' '):
    code.popStack()
    _modifyStackName(code, suffix)

def _pop(oparg, operand, codeSource, code) :
    code.popStack()
_POP_TOP = _PRINT_ITEM = _pop

def _popModified(oparg, operand, codeSource, code):
    _popModifiedStack(code)

def _BINARY_RSHIFT(oparg, operand, codeSource, code):
    _coerce_type(code)
    _popModified(oparg, operand, codeSource, code)
_BINARY_LSHIFT = _BINARY_RSHIFT

def _checkModifyNoOp(code, op, msg=msgs.MODIFY_VAR_NOOP, modifyStack=1):
    stack = code.stack
    if len(stack) >= 2:
        if (stack[-1].type != Stack.TYPE_UNKNOWN and
            stack[-2].type != Stack.TYPE_UNKNOWN):
            name = stack[-1].getName()
            if name != Stack.TYPE_UNKNOWN and name == stack[-2].getName():
                code.addWarning(msg % (name, op, name))

        if modifyStack:
            code.popStack()
            stack[-1].const = 0
            _modifyStackName(code, op)

def _BINARY_AND(oparg, operand, codeSource, code):
    # Don't modify the stack, since _coerce_type() will do it.
    _checkModifyNoOp(code, '&', modifyStack=0)
    _coerce_type(code)

def _BINARY_OR(oparg, operand, codeSource, code):
    # Don't modify the stack, since _coerce_type() will do it.
    _checkModifyNoOp(code, '|', modifyStack=0)
    _coerce_type(code)

def _BINARY_XOR(oparg, operand, codeSource, code):
    # Don't modify the stack, since _coerce_type() will do it.
    _checkModifyNoOp(code, '^', msgs.XOR_VAR_WITH_ITSELF, modifyStack=0)
    _coerce_type(code)

def _PRINT_ITEM_TO(oparg, operand, codeSource, code):
    code.popStackItems(2)

def _PRINT_NEWLINE_TO(oparg, operand, codeSource, code):
    code.popStackItems(1)

try:
    ComplexType = types.ComplexType
except NameError:
    ComplexType = types.FloatType    # need some numeric type here

_NUMERIC_TYPES = (types.IntType, types.FloatType, ComplexType)

# FIXME: This is pathetically weak, need to handle more types
def _coerce_type(code) :
    _checkNoEffect(code)
    newItem = Stack.Item('<stack>', Stack.TYPE_UNKNOWN)
    if len(code.stack) >= 2 :
        s1, s2 = code.stack[-2:]
        s1type = s1.getType(code.typeMap)
        s2type = s2.getType(code.typeMap)
        if s1type != s2type :
            if s1type in _NUMERIC_TYPES and s2type in _NUMERIC_TYPES :
                newType = types.FloatType
                if s1type == ComplexType or s2type == ComplexType:
                    newType = ComplexType
                newItem.type = newType

    code.popStackItems(2)
    code.pushStack(newItem)

def _BINARY_ADD(oparg, operand, codeSource, code) :
    stack = code.stack
    if len(stack) >= 2 and (stack[-1].const and stack[-2].const and
                            stack[-1].type == stack[-2].type) :
        value = stack[-2].data + stack[-1].data
        code.popStackItems(2)
        code.pushStack(Stack.Item(value, type(value), 1))
    else :
        _coerce_type(code)

def _BINARY_SUBTRACT(oparg, operand, codeSource, code) :
    _coerce_type(code)
_BINARY_POWER = _BINARY_SUBTRACT

def _BINARY_SUBSCR(oparg, operand, codeSource, code) :
    _checkNoEffect(code)
    if len(code.stack) >= 2 :
        stack = code.stack
        varType = code.typeMap.get(utils.safestr(stack[-2].data), [])
        if types.ListType in varType and stack[-1].type == types.TupleType :
            code.addWarning(msgs.USING_TUPLE_ACCESS_TO_LIST % stack[-2].data)
    _popStackRef(code, operand)

def _isint(stackItem, code) :
    if type(stackItem.data) == types.IntType :
        return 1
    stackTypes = code.typeMap.get(stackItem.data, [])
    if len(stackTypes) != 1 :
        return 0
    return types.IntType in stackTypes

def _BINARY_DIVIDE(oparg, operand, codeSource, code) :
    _checkNoEffect(code)
    _checkModifyNoOp(code, '/', msgs.DIVIDE_VAR_BY_ITSELF, 0)
    if cfg().intDivide and len(code.stack) >= 2 :
        if _isint(code.stack[-1], code) and _isint(code.stack[-2], code) :
            # don't warn if we are going to convert the result to an int
            if not (len(code.stack) >= 3 and
                    code.stack[-3].data == 'int' and
                    OP.CALL_FUNCTION(code.nextOpInfo()[0])):
                code.addWarning(msgs.INTEGER_DIVISION % tuple(code.stack[-2:]))

    _popModifiedStack(code, '/')

def _BINARY_TRUE_DIVIDE(oparg, operand, codeSource, code) :
    _checkNoEffect(code)
    _checkVariableOperationOnItself(code, operand, msgs.DIVIDE_VAR_BY_ITSELF)
    _popModifiedStack(code, '/')
_BINARY_FLOOR_DIVIDE = _BINARY_TRUE_DIVIDE

def _BINARY_MULTIPLY(oparg, operand, codeSource, code) :
    if len(code.stack) >= 2 :
        formatString = _getFormatString(code, codeSource)
        if formatString and type(code.stack[-1].data) == types.IntType :
            code.stack[-2].data = formatString * code.stack[-1].data
            code.popStack()
        else:
            _coerce_type(code)
    else:
        _popModifiedStack(code, '*')

def _BINARY_MODULO(oparg, operand, codeSource, code) :
    _checkNoEffect(code)
    if cfg().modulo1 and code.stack and code.stack[-1].data == 1:
        if len(code.stack) < 2 or \
           code.stack[-2].getType(code.typeMap) != types.FloatType:
            code.addWarning(msgs.MODULO_1)
    _getFormatWarnings(code, codeSource)
    _popModifiedStack(code, '%')
    if code.stack:
        code.stack[-1].const = 0

def _ROT_TWO(oparg, operand, codeSource, code) :
    if len(code.stack) >= 2 :
        tmp = code.stack[-2]
        code.stack[-2] = code.stack[-1]
        code.stack[-1] = tmp

def _ROT_THREE(oparg, operand, codeSource, code) :
    """Lifts second and third stack item one position up,
       moves top down to position three."""
    if len(code.stack) >= 3 :
        second = code.stack[-2]
        third = code.stack[-3]
        code.stack[-3] = code.stack[-1]
        code.stack[-2] = third
        code.stack[-1] = second

def _ROT_FOUR(oparg, operand, codeSource, code) :
    """Lifts second, third and forth stack item one position up,
       moves top down to position four."""
    if len(code.stack) >= 4 :
        second = code.stack[-2]
        third = code.stack[-3]
        fourth = code.stack[-4]
        code.stack[-4] = code.stack[-1]
        code.stack[-3] = fourth
        code.stack[-2] = third
        code.stack[-1] = second

def _SETUP_EXCEPT(oparg, operand, codeSource, code) :
    code.has_except = 1
    code.pushStack(Stack.Item(None, Stack.TYPE_EXCEPT))
    code.pushStack(Stack.Item(None, Stack.TYPE_EXCEPT))

def _SETUP_FINALLY(oparg, operand, codeSource, code) :
    if not code.has_except :
        code.try_finally_first = 1

# SETUP_WITH added in 2.7
# not sure what _SETUP_FINALLY does exactly, but looking at the 2.6
# implementation for the new SETUP_WITH, it ends with SETUP_FINALLY,
# so SETUP_WITH should do the same
def _SETUP_WITH(oparg, operand, codeSource, code):
    if not code.has_except:
        code.try_finally_first = 1

# WITH_CLEANUP since 2.5
# four stack possibilities:
#    * TOP = None
#    * (TOP, SECOND) = (WHY_{RETURN,CONTINUE}), retval
#    * TOP = WHY_*; no retval below it
#    * (TOP, SECOND, THIRD) = exc_info()

def _WITH_CLEANUP(oparg, operand, codeSource, code):
    if code.stack:
        top = code.stack[-1]
        # FIXME: only implement the first one, only one I've seen
        if top.isNone():
            code.popStack()
        else:
            # FIXME: NotImplementedError gets recaught and reraised with
            # less useful info
            raise IndexError('WITH_CLEANUP with TOS %r' % top)
        
    # pop exit ? I didn't see it in my example case

def _END_FINALLY(oparg, operand, codeSource, code) :
    if code.try_finally_first and code.index == (len(code.bytes) - 4) :
        code.starts_and_ends_with_finally = 1

def _LINE_NUM(oparg, operand, codeSource, code) :
    code.lastLineNum = oparg

def _UNPACK_SEQUENCE(oparg, operand, codeSource, code) :
    code.unpackCount = oparg
    if code.stack:
        top = code.stack[-1]
        # if we know we have a tuple, make sure we unpack it into the
        # right # of variables
        topType = top.getType(code.typeMap)
        if topType in _SEQUENCE_TYPES:
            length = top.length
            # we don't know the length, maybe it's constant and we can find out
            if length == 0:
                value = code.constants.get(utils.safestr(top.data))
                if type(value) in _SEQUENCE_TYPES:
                    length = len(value)
            if length > 0 and length != oparg:
                if cfg().unpackLength:
                    code.addWarning(msgs.WRONG_UNPACK_SIZE % (length, oparg))
        elif topType not in _UNCHECKABLE_STACK_TYPES:
            if cfg().unpackNonSequence:
                code.addWarning(msgs.UNPACK_NON_SEQUENCE %
                                (top.data, _getTypeStr(topType)))
        _modifyStackName(code, '-unpack')

def _SLICE_1_ARG(oparg, operand, codeSource, code) :
    _popStackRef(code, operand)

def _SLICE0(oparg, operand, codeSource, code) :
    # Implements TOS = TOS[:].
    _popStackRef(code, operand, count=1)

_SLICE1 = _SLICE2 = _SLICE_1_ARG

def _SLICE3(oparg, operand, codeSource, code) :
    _popStackRef(code, operand, 3)

def _STORE_SLICE0(oparg, operand, codeSource, code) :
    # FIXME: can we check here if we're storing to something that supports
    # slice assignment ?
    _popStackRef(code, operand, 2)


def _STORE_SLICE1(oparg, operand, codeSource, code) :
    # FIXME: can we check here if we're storing to something that supports
    # slice assignment ?
    _popStackRef(code, operand, 3)

_STORE_SLICE2 = _STORE_SLICE1

def _DELETE_SLICE1(oparg, operand, codeSource, code) :
    # FIXME: can we check here if we're deleting from something that supports
    # slice deletion ?
    _popStackRef(code, operand, count=2)

_DELETE_SLICE2 = _DELETE_SLICE1

def _DELETE_SLICE3(oparg, operand, codeSource, code) :
    # FIXME: can we check here if we're deleting from something that supports
    # slice deletion ?
    _popStackRef(code, operand, 3)

def _check_string_iteration(code, index):
    try:
        item = code.stack[index]
    except IndexError:
        return
    if item.getType(code.typeMap) == types.StringType and \
       cfg().stringIteration:
        code.addWarning(msgs.STRING_ITERATION % item.data)

def _FOR_LOOP(oparg, operand, codeSource, code) :
    code.loops = code.loops + 1
    _check_string_iteration(code, -2)
    _popStackRef(code, '<for_loop>', 2)

def _GET_ITER(oparg, operand, codeSource, code) :
    _check_string_iteration(code, -1)

def _FOR_ITER(oparg, operand, codeSource, code) :
    code.loops = code.loops + 1
    _popStackRef(code, '<for_iter>', 1)

def _jump(oparg, operand, codeSource, code):
    if len(code.stack) >0:
        topOfStack = code.stack[-1]
        if topOfStack.isMethodCall(codeSource.classObject, cfg().methodArgName):
            name = topOfStack.data[-1]
            if codeSource.classObject.methods.has_key(name):
                code.addWarning(msgs.USING_METHOD_AS_ATTR % name)
_JUMP_ABSOLUTE = _jump

def _skip_loops(bytes, i, lastLineNum, max) :
    extended_arg = 0
    blockCount = 1
    while i < max :
        op, oparg, i, extended_arg = OP.getInfo(bytes, i, extended_arg)
        if OP.LINE_NUM(op) :
            lastLineNum = oparg
        elif OP.FOR_LOOP(op) or OP.FOR_ITER(op) or OP.SETUP_LOOP(op) :
            blockCount = blockCount + 1
        elif OP.POP_BLOCK(op) :
            blockCount = blockCount - 1
            if blockCount <= 0 :
                break

    return lastLineNum, i

def _is_unreachable(code, topOfStack, branch, ifFalse) :
    # Are we are checking exceptions, but we not catching all exceptions?
    if (topOfStack.type == Stack.TYPE_COMPARISON and 
        topOfStack.data[1] == 'exception match' and 
        topOfStack.data[2] is not Exception) :
        return 1

    # do we possibly have while 1: ?
    if not (topOfStack.const and topOfStack.data == 1 and ifFalse):
        return 0

    # get the op just before the branch (ie, -3)
    op, oparg, i, extended_arg = OP.getInfo(code.bytes, branch - 3, 0)
    # are we are jumping to before the while 1: (LOAD_CONST, JUMP_IF_FALSE)
    if not (OP.JUMP_ABSOLUTE(op) and oparg == (code.index - 3*3)) :
        return 0

    # check if we break out of the loop
    i = code.index
    lastLineNum = code.getLineNum()
    while i < branch :
        op, oparg, i, extended_arg = OP.getInfo(code.bytes, i, extended_arg)
        if OP.LINE_NUM(op) :
            lastLineNum = oparg
        elif OP.BREAK_LOOP(op) :
            return 0
        elif OP.FOR_LOOP(op) or OP.FOR_ITER(op) or OP.SETUP_LOOP(op) :
            lastLineNum, i = _skip_loops(code.bytes, i, lastLineNum, branch)

    i = code.index - 3*4
    op, oparg, i, extended_arg = OP.getInfo(code.bytes, i, 0)
    if OP.SETUP_LOOP(op) :
        # a little lie to pretend we have a raise after a while 1:
        code.removeBranch(i + oparg)
        code.raiseValues.append((lastLineNum, None, i + oparg))
    return 1

# In Python 2.3, while/if 1: gets optimized to
# ...
# JUMP_FORWARD 4
# JUMP_IF_FALSE ?
# POP_TOP
#
# which generates a Using a conditional statement with a constant value

# JUMP_FORWARD = 110; 4, 0 is the offset (4)
_IGNORE_BOGUS_JUMP = '%c%c%c' % (110, 4, 0)
def _shouldIgnoreBogusJumps(code):
    return _shouldIgnoreCodeOptimizations(code, _IGNORE_BOGUS_JUMP, 6, 3)

def _checkConstantCondition(code, topOfStack, ifFalse, nextIsPop):
    # don't warn when doing (test and 'true' or 'false')
    # still warn when doing (test and None or 'false')
    # since 2.7, instead of JUMP_IF_x/POP_TOP, we have POP_JUMP_IF_x, so
    # the next opcode is not POP_TOP, but a possible LOAD_CONST already.
    candidate = 0
    if nextIsPop:
        candidate = 1

    if ifFalse or not OP.LOAD_CONST(code.nextOpInfo(candidate)[0]) or \
       not topOfStack.data or topOfStack.type is types.NoneType:
        if not _shouldIgnoreBogusJumps(code):
            code.addWarning(msgs.CONSTANT_CONDITION % utils.safestr(topOfStack))
    
def _jump_conditional(oparg, operand, codeSource, code, ifFalse, nextIsPop):
    # FIXME: this doesn't work in 2.3+ since constant conditions
    #        are optimized away by the compiler.
    if code.stack:
        topOfStack = code.stack[-1]
        if (topOfStack.const or topOfStack.type is types.NoneType) and \
           cfg().constantConditions and \
           (topOfStack.data != 1 or cfg().constant1):
            _checkConstantCondition(code, topOfStack, ifFalse, nextIsPop)

        if _is_unreachable(code, topOfStack, code.label, ifFalse):
            code.removeBranch(code.label)

    _jump(oparg, operand, codeSource, code)

# JUMP_IF_FALSE(delta)
#  If TOS is false, increment the bytecode counter by delta. TOS is not changed.
def _JUMP_IF_FALSE(oparg, operand, codeSource, code):
    _jump_conditional(oparg, operand, codeSource, code, 1, 1)

def _JUMP_IF_TRUE(oparg, operand, codeSource, code):
    _jump_conditional(oparg, operand, codeSource, code, 0, 1)

def _JUMP_FORWARD(oparg, operand, codeSource, code):
    _jump(oparg, operand, codeSource, code)
    code.remove_unreachable_code(code.label)

# POP_JUMP_IF_FALSE(target)
# If TOS is false, sets the bytecode counter to target. TOS is popped.
def _POP_JUMP_IF_FALSE(oparg, operand, codeSource, code):
    _jump_conditional(oparg, operand, codeSource, code, 1, 0)
    _pop(oparg, operand, codeSource, code)

def _POP_JUMP_IF_TRUE(oparg, operand, codeSource, code):
    _jump_conditional(oparg, operand, codeSource, code, 0, 0)
    _pop(oparg, operand, codeSource, code)

def _JUMP_IF_FALSE_OR_POP(oparg, operand, codeSource, code):
    # FIXME: can the next one still be a pop ?
    _jump_conditional(oparg, operand, codeSource, code, 1, 0)
    # FIXME: should we really POP here ? We don't know whether the condition
    # is true or false...
    _pop(oparg, operand, codeSource, code)

def _JUMP_IF_TRUE_OR_POP(oparg, operand, codeSource, code):
    _jump_conditional(oparg, operand, codeSource, code, 0, 0)
    # FIXME: same here
    _pop(oparg, operand, codeSource, code)

def _RETURN_VALUE(oparg, operand, codeSource, code) :
    if not codeSource.calling_code :
        code.addReturn()

def _EXEC_STMT(oparg, operand, codeSource, code) :
    if cfg().usesExec :
        if code.stack and code.stack[-1].isNone() :
            code.addWarning(msgs.USES_GLOBAL_EXEC)
        else :
            code.addWarning(msgs.USES_EXEC)

def _YIELD_VALUE(oparg, operand, codeSource, code) :
    # FIXME: any kind of checking we need to do on a yield ? globals ?
    code.popStack()

def _checkStrException(code, varType, item):
    if varType is types.StringType:
        code.addWarning(msgs.RAISE_STR_EXCEPTION % item.data)

def _RAISE_VARARGS(oparg, operand, codeSource, code) :
    code.addRaise()
    if not cfg().badExceptions:
        return

    if oparg > 0 and len(code.stack) >= oparg:
        item = code.stack[-oparg]
        if item.type not in (Stack.TYPE_FUNC_RETURN, Stack.TYPE_UNKNOWN):
            if item.type is Stack.TYPE_GLOBAL:
                e, is_str = _getExceptionInfo(codeSource, item)
                if is_str:
                    _checkStrException(code, e.type, item)
                elif e is not None and not _isexception(e):
                    code.addWarning(msgs.RAISE_BAD_EXCEPTION % item.data)
            else:
                _checkStrException(code, item.getType(code.typeMap), item)

def _SET_ADD(oparg, operand, codeSource, code):
    code.popStackItems(1)

def _MAP_ADD(oparg, operand, codeSource, code):
    code.popStackItems(2)

def _empty(oparg, operand, codeSource, code): pass
def _unimplemented(oparg, operand, codeSource, code):
    raise NotImplementedError('No DISPATCH member for operand')

# these op codes do not interact with the stack
_PRINT_NEWLINE = _empty
_LOAD_LOCALS = _empty
_POP_BLOCK = _empty
_BREAK_LOOP = _empty
_SETUP_LOOP = _empty
_CONTINUE_LOOP = _empty
_STORE_DEREF = _empty
_STOP_CODE = _empty
_NOP = _empty

# FIXME: all these could use an implementation
_INPLACE_FLOOR_DIVIDE = _INPLACE_TRUE_DIVIDE = _unimplemented
_EXTENDED_ARG = _unimplemented
_PRINT_EXPR = _unimplemented

_DELETE_SLICE0 = _unimplemented
_STORE_SLICE3 = _unimplemented

# new in 2.7
_BUILD_SET = _unimplemented

# dispatched from pychecker/warn.py
DISPATCH = [ None ] * 256
DISPATCH[  0] = _STOP_CODE
DISPATCH[  1] = _POP_TOP
DISPATCH[  2] = _ROT_TWO
DISPATCH[  3] = _ROT_THREE
DISPATCH[  4] = _DUP_TOP
DISPATCH[  5] = _ROT_FOUR
DISPATCH[  9] = _NOP            # since Python 2.4
DISPATCH[ 10] = _UNARY_POSITIVE
DISPATCH[ 11] = _UNARY_NEGATIVE
DISPATCH[ 12] = _UNARY_NOT
DISPATCH[ 13] = _UNARY_CONVERT
DISPATCH[ 15] = _UNARY_INVERT
DISPATCH[ 18] = _LIST_APPEND
DISPATCH[ 19] = _BINARY_POWER
DISPATCH[ 20] = _BINARY_MULTIPLY
DISPATCH[ 21] = _BINARY_DIVIDE
DISPATCH[ 22] = _BINARY_MODULO
DISPATCH[ 23] = _BINARY_ADD
DISPATCH[ 24] = _BINARY_SUBTRACT
DISPATCH[ 25] = _BINARY_SUBSCR
DISPATCH[ 26] = _BINARY_FLOOR_DIVIDE
DISPATCH[ 27] = _BINARY_TRUE_DIVIDE
DISPATCH[ 28] = _INPLACE_FLOOR_DIVIDE
DISPATCH[ 29] = _INPLACE_TRUE_DIVIDE
DISPATCH[ 30] = _SLICE0
DISPATCH[ 31] = _SLICE1
DISPATCH[ 32] = _SLICE2
DISPATCH[ 33] = _SLICE3
DISPATCH[ 40] = _STORE_SLICE0
DISPATCH[ 41] = _STORE_SLICE1
DISPATCH[ 42] = _STORE_SLICE2
DISPATCH[ 43] = _STORE_SLICE3
DISPATCH[ 50] = _DELETE_SLICE0
DISPATCH[ 51] = _DELETE_SLICE1
DISPATCH[ 52] = _DELETE_SLICE2
DISPATCH[ 53] = _DELETE_SLICE3
DISPATCH[ 54] = _STORE_MAP              # Since Python 2.6
DISPATCH[ 55] = _BINARY_ADD             # INPLACE
DISPATCH[ 56] = _BINARY_SUBTRACT        # INPLACE
DISPATCH[ 57] = _BINARY_MULTIPLY        # INPLACE
DISPATCH[ 58] = _BINARY_DIVIDE          # INPLACE
DISPATCH[ 59] = _BINARY_MODULO          # INPLACE
DISPATCH[ 60] = _STORE_SUBSCR
DISPATCH[ 61] = _DELETE_SUBSCR
DISPATCH[ 62] = _BINARY_LSHIFT
DISPATCH[ 63] = _BINARY_RSHIFT
DISPATCH[ 64] = _BINARY_AND
DISPATCH[ 65] = _BINARY_XOR
DISPATCH[ 66] = _BINARY_OR
DISPATCH[ 67] = _BINARY_POWER           # INPLACE
DISPATCH[ 68] = _GET_ITER
DISPATCH[ 70] = _PRINT_EXPR
DISPATCH[ 71] = _PRINT_ITEM
DISPATCH[ 72] = _PRINT_NEWLINE
DISPATCH[ 73] = _PRINT_ITEM_TO
DISPATCH[ 74] = _PRINT_NEWLINE_TO
DISPATCH[ 75] = _BINARY_LSHIFT          # INPLACE
DISPATCH[ 76] = _BINARY_RSHIFT          # INPLACE
DISPATCH[ 77] = _BINARY_AND             # INPLACE
DISPATCH[ 78] = _BINARY_XOR             # INPLACE
DISPATCH[ 79] = _BINARY_OR              # INPLACE
DISPATCH[ 80] = _BREAK_LOOP
DISPATCH[ 81] = _WITH_CLEANUP           # Since Python 2.5
DISPATCH[ 82] = _LOAD_LOCALS
DISPATCH[ 83] = _RETURN_VALUE
DISPATCH[ 84] = _IMPORT_STAR
DISPATCH[ 85] = _EXEC_STMT
DISPATCH[ 86] = _YIELD_VALUE
DISPATCH[ 87] = _POP_BLOCK
DISPATCH[ 88] = _END_FINALLY
DISPATCH[ 89] = _BUILD_CLASS
DISPATCH[ 90] = _STORE_NAME
DISPATCH[ 91] = _DELETE_NAME
DISPATCH[ 92] = _UNPACK_SEQUENCE
DISPATCH[ 93] = _FOR_ITER
# changed from no arguments to taking an argument and 18 to 94 in 2.7
# Python svn revision 67818
DISPATCH[ 94] = _LIST_APPEND_2_7
DISPATCH[ 95] = _STORE_ATTR
DISPATCH[ 96] = _DELETE_ATTR
DISPATCH[ 97] = _STORE_GLOBAL
DISPATCH[ 98] = _DELETE_GLOBAL
DISPATCH[ 99] = _DUP_TOPX
DISPATCH[100] = _LOAD_CONST
DISPATCH[101] = _LOAD_NAME
DISPATCH[102] = _BUILD_TUPLE
DISPATCH[103] = _BUILD_LIST

if utils.pythonVersion() >= utils.PYTHON_2_7:
    DISPATCH[104] = _BUILD_SET
    DISPATCH[105] = _BUILD_MAP
    DISPATCH[106] = _LOAD_ATTR
    DISPATCH[107] = _COMPARE_OP
    DISPATCH[108] = _IMPORT_NAME
    DISPATCH[109] = _IMPORT_FROM
else:
    DISPATCH[104] = _BUILD_MAP
    DISPATCH[105] = _LOAD_ATTR
    DISPATCH[106] = _COMPARE_OP
    DISPATCH[107] = _IMPORT_NAME
    DISPATCH[108] = _IMPORT_FROM

DISPATCH[110] = _JUMP_FORWARD

if utils.pythonVersion() >= utils.PYTHON_2_7:
    DISPATCH[111] = _POP_JUMP_IF_FALSE
    DISPATCH[112] = _POP_JUMP_IF_TRUE
else:
    DISPATCH[111] = _JUMP_IF_FALSE
    DISPATCH[112] = _JUMP_IF_TRUE

DISPATCH[113] = _JUMP_ABSOLUTE

if utils.pythonVersion() >= utils.PYTHON_2_7:
    DISPATCH[114] = _JUMP_IF_FALSE_OR_POP
    DISPATCH[115] = _JUMP_IF_TRUE_OR_POP
else:
    DISPATCH[114] = _FOR_LOOP

DISPATCH[116] = _LOAD_GLOBAL
DISPATCH[119] = _CONTINUE_LOOP
DISPATCH[120] = _SETUP_LOOP
DISPATCH[121] = _SETUP_EXCEPT
DISPATCH[122] = _SETUP_FINALLY
DISPATCH[124] = _LOAD_FAST
DISPATCH[125] = _STORE_FAST
DISPATCH[126] = _DELETE_FAST
DISPATCH[127] = _LINE_NUM
DISPATCH[130] = _RAISE_VARARGS
DISPATCH[131] = _CALL_FUNCTION
DISPATCH[132] = _MAKE_FUNCTION
DISPATCH[133] = _BUILD_SLICE
DISPATCH[134] = _MAKE_CLOSURE
DISPATCH[135] = _LOAD_CLOSURE
DISPATCH[136] = _LOAD_DEREF
DISPATCH[137] = _STORE_DEREF
DISPATCH[140] = _CALL_FUNCTION_VAR
DISPATCH[141] = _CALL_FUNCTION_KW
DISPATCH[142] = _CALL_FUNCTION_VAR_KW

# changed from 143 to 145 in 2.7, because 143 is now _SETUP_WITH
# Python svn revision 72912
if utils.pythonVersion() >= utils.PYTHON_2_7:
    DISPATCH[143] = _SETUP_WITH
    DISPATCH[145] = _EXTENDED_ARG
else:
    DISPATCH[143] = _EXTENDED_ARG

# Added in 2.7
# Python svn revision 77422
DISPATCH[146] = _SET_ADD
DISPATCH[147] = _MAP_ADD
