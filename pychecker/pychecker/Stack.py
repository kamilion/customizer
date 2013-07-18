# -*- Mode: Python -*-
# vi:si:et:sw=4:sts=4:ts=4

# Copyright (c) 2001-2002, MetaSlash Inc.  All rights reserved.

"""
Module to hold manipulation of elements on the stack.
"""

import types
from pychecker import utils

DATA_UNKNOWN = "-unknown-"
LOCALS = 'locals'

# These should really be defined by subclasses
TYPE_UNKNOWN = "-unknown-"
TYPE_FUNC_RETURN = "-return-value-"
TYPE_ATTRIBUTE = "-attribute-"
TYPE_COMPARISON = "-comparison-"
TYPE_GLOBAL = "-global-"
TYPE_EXCEPT = "-except-"

class Item:
    """
    Representation of data on the stack

    @ivar is_really_string: whether the stack item really is a string.
    """

    def __init__(self, data, dataType, const=0, length=0):
        """
        @param data:     the actual data of the stack item
        @type  dataType: type
        @param const:    whether the item is a constant or not
        @type  const:    int
        @type  length:   int
        """

        self.data = data
        self.type = dataType
        self.const = const
        self.length = length
        self.is_really_string = 0

    def __str__(self) :
        if type(self.data) == types.TupleType:
            value = '('
            for item in self.data:
                value = value + utils.safestr(item) + ', '
            # strip off the ', ' for multiple items
            if len(self.data) > 1:
                value = value[:-2]
            return value + ')'
        return utils.safestr(self.data)

    def __repr__(self):
        return 'Stack Item: (%r, %r, %d)' % (self.data, self.type, self.const)

    def isNone(self):
        return (self.type != TYPE_UNKNOWN and self.data is None or
                (self.data == 'None' and not self.const))

    def isImplicitNone(self) :
        return self.data is None and self.const

    def isMethodCall(self, c, methodArgName):
        return self.type == TYPE_ATTRIBUTE and c != None and \
               len(self.data) == 2 and self.data[0] == methodArgName

    def isLocals(self):
        return self.type == types.DictType and self.data == LOCALS

    def setStringType(self, value = types.StringType):
        self.is_really_string = value == types.StringType

    def getType(self, typeMap):
        """
        @type  typeMap: dict of str -> list of str or L{pcmodules.Class}
        """

        # FIXME: looks like StringType is used for real strings but also
        # for names of objects.  Couldn't this be split to avoid
        # self.is_really_string ?
        if self.type != types.StringType or self.is_really_string:
            return self.type

        # FIXME: I assert here because there were if's to this effect,
        # and a return of type(self.data).  Remove this assert later.
        assert type(self.data) == types.StringType

        # it's a StringType but not really a string
        # if it's constant, return type of data
        if self.const:
            return types.StringType


        # it's a non-constant StringType, so treat it as the name of a token
        # and look up the actual type in the typeMap
        localTypes = typeMap.get(self.data, [])
        if len(localTypes) == 1:
            return localTypes[0]

        return TYPE_UNKNOWN

    def getName(self):
        if self.type == TYPE_ATTRIBUTE and type(self.data) != types.StringType:
            strValue = ""
            # convert the tuple into a string ('self', 'data') -> self.data
            for item in self.data:
                strValue = '%s.%s' % (strValue, utils.safestr(item))
            return strValue[1:]
        return utils.safestr(self.data)

    def addAttribute(self, attr):
        if type(self.data) == types.TupleType:
            self.data = self.data + (attr,)
        else:
            self.data = (self.data, attr)
        self.type = TYPE_ATTRIBUTE


# FIXME: I haven't seen makeDict with anything else than (), 1
def makeDict(values=(), const=1):
    """
    @param values: the values to make a dict out of
    @type  values: FIXME: tuple of L{Item} ?
    @param const:  whether the dict is constant

    @returns: A Stack.Item representing a dict
    @rtype:   L{Item}
    """
    values = tuple(values)
    if not values:
        values = ('<on-stack>', )
    return Item(values, types.DictType, const, len(values))

def makeTuple(values=(), const=1):
    """
    @param values: the values to make a tuple out of
    @type  values: tuple of L{Item}
    @param const:  whether the tuple is constant

    @returns: A Stack.Item representing a tuple
    @rtype:   L{Item}
    """
    return Item(tuple(values), types.TupleType, const, len(values))

# FIXME: I haven't seen makeList with anything else than const=1
def makeList(values=[], const=1):
    """
    @param values: the values to make a list out of
    @type  values: list of L{Item}
    @param const:  whether the list is constant

    @returns: A Stack.Item representing a list
    @rtype:   L{Item}
    """
    return Item(values, types.ListType, const, len(values))

def makeFuncReturnValue(stackValue, argCount) :
    data = DATA_UNKNOWN
    # vars() without params == locals()
    if stackValue.type == TYPE_GLOBAL and \
       (stackValue.data == LOCALS or
        (argCount == 0 and stackValue.data == 'vars')) :
        data = LOCALS
    return Item(data, TYPE_FUNC_RETURN)

def makeComparison(stackItems, comparison) :
    return Item((stackItems[0], comparison, stackItems[1]), TYPE_COMPARISON)

