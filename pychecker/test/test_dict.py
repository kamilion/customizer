# -*- Mode: Python -*-
# vi:si:et:sw=4:sts=4:ts=4

'''
Tests related to dicts.
'''

import unittest
import common

class KeysTestCase(common.TestCase):
    '''
    test that modules with the same name do not shadow eachother.
    '''
    def test_dict(self):
        self.check('test_dict')
    
if __name__ == '__main__':
    unittest.main()
