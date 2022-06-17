#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Github: @felipsandoval
# para ejecutar: python3 -m unittest <nombre del fichero test_XXX.py>

from duplicateScripts import *
import unittest

class TestCuboid(unittest.TestCase):
    def test_volume(self):
        self.assertAlmostEqual(cuboid_volume(2),8)
        self.assertAlmostEqual(cuboid_volume(1),1)
        self.assertAlmostEqual(cuboid_volume(0),0)
    
    def test_input_value(self):
        self.assertRaises(TypeError, cuboid_volume, True)

#unittest.main(argv=[''],verbosity=2, exit=False)