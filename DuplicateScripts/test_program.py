#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Github: @felipsandoval
# To run with module: python3 -m unittest <test_XXX.py>
# Also run with: python3 <test_XXX.py>
# Run all test with: python -m unittest discover

from program import *
import unittest


class TestProgram(unittest.TestCase):
    def test_obtaining_json(self):
        self.assertEqual(obtaining_json("project.json"),
                         json.loads(open("project.json").read()))
        self.assertEqual(obtaining_json("test_projects.zip"),
                         ['490593149.json', '490593198.json',
                          '490593289.json'])
        self.assertEqual(obtaining_json("test.sb3"),
                         json.loads(open("project.json").read()))
        self.assertNotEqual(obtaining_json("test.sb3"), "project.json")

    def test_sb3_json_extraction(self):
        self.assertEqual(sb3_json_extraction("test.sb3"),
                         json.loads(open("project.json").read()))


if __name__ == "__main__":
    unittest.main()
