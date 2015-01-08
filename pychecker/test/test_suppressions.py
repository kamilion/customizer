# -*- Mode: Python -*-
# vi:si:et:sw=4:sts=4:ts=4

'''
Tests related to suppressions.
'''

import unittest
import common

class NestedTestCase(common.TestCase):
    '''
    Test that suppressions inside nested code stay inside their
    context.
    '''
    def test_getmodule(self):
        self.check('test_nestedsuppression', '--objattrs')
    
if __name__ == '__main__':
    unittest.main()
