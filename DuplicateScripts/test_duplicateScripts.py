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

        self.assertRaises(KeyError, get_next_blocks, None,
                          {"loop": {"next": None}, "empty": {"next": "Wrong"}})

    def test_change_blockid(self):
        self.assertEqual(change_blockid([["A", "B", "C"], ["D", "E", "F"]],
                                        {"A": "a", "B": "b", "C": "c",
                                        "D": "d", "E": "e", "F": "f"},
                                        False),
                         0)

        self.assertEqual(change_blockid([["A", "B", "C"], ["D", "E", "F"]],
                                        {"A": "a", "B": "b", "C": "c",
                                        "D": "looks_size", "E": "looks_size",
                                         "F": "looks_costume"},
                                        False),
                         0)

        self.assertEqual(change_blockid([["A", "B", "C"], ["D", "E", "F"]],
                                        {"A": "a", "B": "b", "C": "c",
                                        "D": "looks_size", "E": "looks_size",
                                         "F": "looks_costume"},
                                        True),
                         3)

        self.assertNotEqual(change_blockid([["A", "B", "C"], ["D", "E", "F"]],
                                           {"A": "a", "B": "b", "C": "c",
                                            "D": "looks_size",
                                            "E": "looks_size",
                                            "F": "looks_costume"},
                                           True),
                            2)

    def test_getloop_ids(self):
        self.assertEqual(getloop_ids({'opcode': 'control_repeat', 'next': None,
                                      'inputs': {'SUBSTACK3': [2, 'uno']}},
                                     {"uno": {"next": "dos"},
                                      "dos": {"next": "tres"},
                                      "tres": {"next": "cuatro"},
                                      "cuatro": {"next": None}},
                                     "control_repeat"),
                         ["control_repeat", "END_LOOP"])

        self.assertEqual(getloop_ids({'opcode': 'control_if', 'next': None,
                                      'inputs': {'SUBSTACK': [2, 'uno']}},
                                     {"uno": {"next": "dos"},
                                      "dos": {"next": "tres"},
                                      "tres": {"next": "cuatro"},
                                      "cuatro": {"next": None}},
                                     "control_if"),
                         ["control_if", "uno", "dos", "tres", "cuatro",
                          "END_IF", "END_LOOP"])

        self.assertNotEqual(getloop_ids({'opcode': 'control_if', 'next': None,
                                         'inputs': {'SUBSTACK': [2, 'uno']}},
                                        {"uno": {"next": "dos"},
                                         "dos": {"next": "tres"},
                                         "tres": {"next": "cuatro"},
                                         "cuatro": {"next": None}},
                                        "control_if"),
                            ["control_if", "uno", "dos", "tres", "cuatro",
                             "END_LOOP"])


if __name__ == "__main__":
    unittest.main()
