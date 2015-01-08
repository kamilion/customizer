# -*- Mode: Python -*-
# vi:si:et:sw=4:sts=4:ts=4

'''
Tests related to dicts.
'''

import unittest
import common

class KeysTestCase(common.TestCase):
    '''
    test that globals are only warned once without -g.
    '''
    def test_global(self):
        self.check('test_global')

    def test_global_g(self):
        self.check('test_global', args='-g')
    
if __name__ == '__main__':
    unittest.main()
