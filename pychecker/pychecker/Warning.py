# -*- Mode: Python -*-
# vi:si:et:sw=4:sts=4:ts=4

# Copyright (c) 2001, MetaSlash Inc.  All rights reserved.
# Portions Copyright (c) 2005, Google, Inc. All rights reserved.

"""
Warning class to hold info about each warning.
"""


class Warning :
    """
    Class which holds warning information.

    @ivar file: file where the warning was found.
    @type file: str
    @ivar line: line number where the warning was found.
    @type line: int
    @type err:  L{msgs.WarningClass}
    """

    def __init__(self, file, line, err) :
        """
        @param file: an object from which the file where the warning
                     was found can be derived
        @type  file: L{types.CodeType}, L{function.FakeCode} or str
        @param line: the line where the warning was found; if file was str,
                     then line will be a code object.
        @type  line: int or L{types.CodeType} or None
        @type  err:  L{msgs.WarningClass}
        """
        if hasattr(file, "function") :
            # file is a function.FakeCode
            file = file.function.func_code.co_filename
        elif hasattr(file, "co_filename") :
            # file is a types.CodeType
            file = file.co_filename
        elif hasattr(line, "co_filename") :
            # file was a str
            file = line.co_filename
        if file[:2] == './' :
            file = file[2:]
        self.file = file

        if hasattr(line, "co_firstlineno") :
            line = line.co_firstlineno
        if line == None :
            line = 1
        self.line = line
        self.err = err
        self.level = err.level

    def __cmp__(self, warn) :
        if warn == None :
            return 1
        if not self.file and not self.line:
            return 1
        if self.file != warn.file :
            return cmp(self.file, warn.file)
        if self.line != warn.line :
            return cmp(self.line, warn.line)
        return cmp(self.err, warn.err)

    def format(self, removeSysPath=True) :
        if not self.file and not self.line:
            return str(self.err)
        file = self.file
        if removeSysPath:
            import sys
            for path in sys.path:
                if not path or path == '.':
                    continue
                if file.startswith(path):
                    file = '[system path]' + file[len(path):]
        
        return "%s:%d: %s" % (file, self.line, self.err)

    def output(self, stream, removeSysPath=True) :
        stream.write(self.format(removeSysPath) + "\n")
