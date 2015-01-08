# -*- Mode: Python; test-case-name: test.test_pychecker_function -*-
# vi:si:et:sw=4:sts=4:ts=4

'''
Tests related to pychecker.function
'''

import unittest
import common

from pychecker import function, utils

class GeneratorTestCase(common.TestCase):
    '''
    Test that a generator function works as expected.
    '''
    def testGenerator(self):
        def returner():
            return (str(x) for x in range(10))

        # get the generator code object
        genCode = returner.func_code.co_consts[1]

        # FIXME: this is what co_varnames looks like, but I don't understand why
        # possible clue in Python, Lib/compiler/ast.py, class GenExpr
        if utils.pythonVersion() < utils.PYTHON_2_5:
            self.assertEquals(genCode.co_varnames, ('[outmost-iterable]', 'x'))
        else:
            self.assertEquals(genCode.co_varnames, ('.0', 'x'))

        # wrap it into a Funtion so we can look at it
        f = function.Function(
            function.FakeFunction(genCode.co_name, genCode))

        self.failIf(f.isMethod)
        self.assertEquals(f.minArgs, 1)
        self.assertEquals(f.maxArgs, 1)
        if utils.pythonVersion() < utils.PYTHON_2_5:
            self.assertEquals(f.arguments(), ('[outmost-iterable]', ))
        else:
            self.assertEquals(f.arguments(), ('.0', ))

if __name__ == '__main__':
    unittest.main()
