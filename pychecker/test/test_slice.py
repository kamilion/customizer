# -*- Mode: Python -*-
# vi:si:et:sw=4:sts=4:ts=4

'''
Tests related to slices.
'''

import unittest
import common

class SliceTestCase:#(common.TestCase):
    '''
    test that slices work.
    '''
    def test_slice(self):
        self.check('test_slice')
    
if __name__ == '__main__':
    unittest.main()
