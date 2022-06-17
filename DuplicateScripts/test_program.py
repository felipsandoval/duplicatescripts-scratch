#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Github: @felipsandoval
# para ejecutar: python3 -m unittest <nombre del fichero test_XXX.py>
# python -m unittest discover -- 
# esto ejecutará TODOS los ficheros cuyo nombre empiecen por test y los ejecutará

from program import *
import unittest

class TestProgram(unittest.TestCase):
    def test_obtaining_json(self):
        self.assertRaises(TypeError, obtaining_json, True)

#unittest.main(argv=[''],verbosity=2, exit=False)