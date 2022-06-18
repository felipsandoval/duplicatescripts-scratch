#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Github: @felipsandoval
# To run with module: python3 -m unittest <test_XXX.py>
# Also run with: python3 <test_XXX.py>
# Run all test with: python -m unittest discover

from duplicateScripts import *
import unittest


class TestDuplicateScripts(unittest.TestCase):
    def test_find_dups(self):
        self.assertEqual(find_dups(["a,b,c,d"]), [])
    
    def test_blocks2ignore(self):
        self.assertEqual(blocks2ignore(), open('IgnoreBlocks.txt').read().splitlines())

if __name__ == "__main__":
    unittest.main()
