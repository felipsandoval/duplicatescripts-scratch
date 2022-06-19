#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Github: @felipsandoval
# To run with module: python3 -m unittest <test_XXX.py>
# Also run with: python3 <test_XXX.py>
# Run all test with: python -m unittest discover

from most_frequent_blocks import *
import unittest


class TestMostFrequentBlocks(unittest.TestCase):
    def test_main(self):
        self.assertNotEqual(main(json.loads(open("test.json",
                                 encoding="utf8").read())), "")


if __name__ == "__main__":
    unittest.main()
