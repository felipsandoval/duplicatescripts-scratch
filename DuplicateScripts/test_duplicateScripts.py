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

        self.assertEqual(getloop_ids({'opcode': 'control_if_else', 'next': "a",
                                      'inputs': {'SUBSTACK': [2, 'uno'],
                                                 'SUBSTACK2': [2, 'tres']}},
                                     {"uno": {"next": "dos"},
                                      "dos": {"next": None},
                                      "tres": {"next": "cuatro"},
                                      "cuatro": {"next": None}},
                                     "control_if_else"),
                         ["control_if_else", "uno", "dos", "END_IF",
                          "tres", "cuatro", "END_ELSE", "END_LOOP"])

        self.assertEqual(getloop_ids({'opcode': 'control_if_else', 'next': "a",
                                      'inputs': {'SUBSTACK': [2, 'uno']}},
                                     {"uno": {"next": "dos"},
                                      "dos": {"next": None},
                                      "tres": {"next": "cuatro"},
                                      "cuatro": {"next": None}},
                                     "control_if_else"),
                         ["control_if_else", "uno", "dos", "END_IF",
                          "END_ELSE", "END_LOOP"])

        self.assertNotEqual(getloop_ids({'opcode': 'control_if_else',
                                         'inputs': {'SUBSTACK': [2, 'uno']}},
                                        {"uno": {"next": "dos"},
                                         "dos": {"next": None},
                                         "tres": {"next": "cuatro"},
                                         "cuatro": {"next": None}},
                                        "control_if_else"),
                            ["control_if_else", "uno", "dos", "END_IF",
                             "END_LOOP"])

        self.assertEqual(getloop_ids({'opcode': 'control_if_else', 'next': "a",
                                      'inputs': {'SUBSTAC2K': [2, None]}},
                                     {"uno": {"next": None},
                                      "dos": {"next": None},
                                      "tres": {"next": "cuatro"},
                                      "cuatro": {"next": None}},
                                     "control_if_else"),
                         ["control_if_else", "END_IF", "END_ELSE", "END_LOOP"])

    def test_add_loop_block(self):
        self.assertEqual(add_loop_block({'3': ["4", "b", "i", "e", "n"]},
                                        {"A": [["1", "2", "3", "4"]],
                                         "B": [["9", "10"], ["11", "12"]],
                                         "C": [["21", "22", "23", "24"]]},
                                        "A"),
                         {"A": [["1", "2", "3", "4", "b", "i", "e", "n"]],
                          "B": [["9", "10"], ["11", "12"]],
                          "C": [["21", "22", "23", "24"]]})

        self.assertEqual(add_loop_block({'10': ["b", "i", "e", "n"]},
                                        {"A": [["1", "2", "3", "4"]],
                                         "B": [["9", "10"], ["11", "12"]],
                                         "C": [["21", "22", "23", "24"]]},
                                        "B"),
                         {"A": [["1", "2", "3", "4"]],
                          "B": [["9", "10", "b", "i", "e", "n"], ["11", "12"]],
                          "C": [["21", "22", "23", "24"]]})

        self.assertEqual(add_loop_block({'1': ["2", "3", "4", "b", "i",
                                               "e", "n"]},
                                        {"A": [["1", "2", "3", "4"]],
                                         "B": [["9", "10"], ["11", "12"]],
                                         "C": [["21", "22", "23", "24"]]},
                                        "A"),
                         {"A": [["1", "2", "3", "4", "b", "i", "e",
                                 "n", "3", "4"]],
                          "B": [["9", "10"], ["11", "12"]],
                          "C": [["21", "22", "23", "24"]]})

        self.assertNotEqual(add_loop_block({'3': ["4", "b", "i", "e", "n"]},
                                           {"A": [["1", "2", "3", "4"]],
                                            "B": [["9", "10"], ["11", "12"]],
                                            "C": [["21", "22", "23", "24"]]},
                                           "A"),
                            {"A": [["1", "2", "3", "b", "i", "e", "n"]],
                             "B": [["9", "10"], ["11", "12"]],
                             "C": [["21", "22", "23", "24"]]})

    def test_custominfo(self):
        self.assertEqual(get_custominfo({'parent': "0",
                                         'mutation': {'proccode': "A",
                                                      'argumentnames': "B"}}),
                         {"type": "procedures_prototype",
                          "custom_name": "A",
                          "argument_names": "B",
                          "n_calls": 0, "blocks": "0"})

        self.assertNotEqual(get_custominfo({'mutation': {'proccode': "A",
                                                         'argumentnames': "B"}
                                            }),
                            {"type": "procedures_prototype",
                             "custom_name": "A",
                             "argument_names": "B",
                             "n_calls": 0, "blocks": "0"})

        self.assertEqual(get_custominfo({'mutation': {'proccode': "A",
                                                      'argumentnames': "B"}
                                         }),
                         {"type": "procedures_prototype",
                          "custom_name": "A",
                          "argument_names": "B",
                          "n_calls": 0, "blocks": "empty"})

        self.assertEqual(get_custominfo({'mutation': {'proccode': "A",
                                                      'argumentnames': "B"}
                                         }),
                         {"type": "procedures_prototype",
                          "custom_name": "A",
                          "argument_names": "B",
                          "n_calls": 0, "blocks": "empty"})

        self.assertRaises(KeyError, get_custominfo,
                          {'any': {'proccode': "A", 'argumentnames': "B"}})

        self.assertRaises(KeyError, get_custominfo,
                          {'mutation': {'any': "A", 'argumentnames': "B"}})

        self.assertRaises(KeyError, get_custominfo,
                          {'mutation': {'proccode': "A", 'any': "B"}})

    def test_custom_was_called(self):
        self.assertEqual(custom_was_called({'opcode': 'procedures_call',
                                            'mutation': {'proccode': 'A'}},
                                           {'Stage': [],
                                            'Objeto1': [{'type': 'test',
                                                         'custom_name': 'A',
                                                         'n_calls': 0,
                                                         'blocks': 'any'}]},
                                           "Objeto1"),
                         {'Stage': [],
                          'Objeto1': [{'type': 'test',
                                       'custom_name': 'A',
                                       'n_calls': 1, 'blocks': 'any'}]})

        self.assertEqual(custom_was_called({'opcode': 'procedures_call',
                                            'mutation': {'proccode': 'A'}},
                                           {'Stage': [],
                                            'Objeto1': [{'type': 'test',
                                                         'custom_name': 'A',
                                                         'n_calls': 5,
                                                         'blocks': 'any'}]},
                                           "Objeto1"),
                         {'Stage': [],
                          'Objeto1': [{'type': 'test',
                                       'custom_name': 'A',
                                       'n_calls': 6, 'blocks': 'any'}]})

        self.assertNotEqual(custom_was_called({'opcode': 'procedures_call',
                                               'mutation': {'proccode': 'A'}},
                                              {'Stage': [],
                                               'Objeto1': [{'type': 'test',
                                                            'custom_name': 'A',
                                                            'n_calls': 3,
                                                            'blocks': 'any'}]},
                                              "Objeto1"),
                            {'Stage': [],
                             'Objeto1': [{'type': 'test',
                                          'custom_name': 'A',
                                          'n_calls': 6, 'blocks': 'any'}]})

        self.assertRaises(KeyError, custom_was_called,
                          {'mutation': {'': 'A'}},
                          {'Stage': [], 'Objeto1': [{'type': 'test',
                                                     'custom_name': 'A',
                                                     'n_calls': 3,
                                                     'blocks': 'any'}]},
                          "Objeto1")

        self.assertRaises(KeyError, custom_was_called,
                          {'A': {'proccode': 'A'}},
                          {'Stage': [], 'Objeto1': [{'type': 'test',
                                                     'custom_name': 'A',
                                                     'n_calls': 3,
                                                     'blocks': 'any'}]},
                          "Objeto1")

        self.assertRaises(KeyError, custom_was_called,
                          {'mutation': {'proccode': 'A'}},
                          {'Stage': [], 'Objeto1': [{'type': 'test',
                                                     'custom': 'B',
                                                     'n_calls': 3,
                                                     'blocks': 'any'}]},
                          "Objeto1")

        self.assertRaises(KeyError, custom_was_called,
                          {'mutation': {'proccode': 'A'}},
                          {'Stage': [], 'Objeto1': [{'type': 'test',
                                                     'custom_name': 'A',
                                                     'calls': 3,
                                                     'blocks': 'any'}]},
                          "Objeto1")


if __name__ == "__main__":
    unittest.main()
