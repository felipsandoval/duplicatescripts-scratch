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
        self.assertEqual(blocks2ignore(),
                         open('IgnoreBlocks.txt').read().splitlines())

    def test_get_next_blocks(self):
        self.assertEqual(get_next_blocks("uno", {"uno": {"next": "dos"},
                                                 "dos": {"next": "tres"},
                                                 "tres": {"next": "cuatro"},
                                                 "cuatro": {"next": None}}),
                         ["uno", "dos", "tres", "cuatro"])

        self.assertNotEqual(get_next_blocks("uno", {"uno": {"next": "tres"},
                                                    "dos": {"next": None},
                                                    "tres": {"next": "dos"},
                                                    "cuatro": {"next": None}}),
                            ["uno", "dos", "tres"])

        self.assertEqual(get_next_blocks("A", {"A": {"next": "B"},
                                                 "B": {"next": "C"},
                                                 "C": {"next": None},
                                                 "D": {"next": "A"}}),
                         ["A", "B", "C"])

        self.assertEqual(get_next_blocks("loop", {"loop": {"next": None},
                                                    "empty": {"next": "Wrong"}}),
                            ["loop"])
 


if __name__ == "__main__":
    unittest.main()
