#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Github: @felipsandoval
# To run with module: python3 -m unittest <test_XXX.py>
# Also run with: python3 <test_XXX.py>
# Run all test with: python -m unittest discover

from duplicateScripts import *
import unittest


class TestCuboid(unittest.TestCase):
    def test_volume(self):
        self.assertAlmostEqual(cuboid_volume(2), 8)
        self.assertAlmostEqual(cuboid_volume(1), 1)
        self.assertAlmostEqual(cuboid_volume(0), 0)

    def test_input_value(self):
        self.assertRaises(TypeError, cuboid_volume, True)


if __name__ == "__main__":
    unittest.main()
