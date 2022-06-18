#!/usr/bin/python3
# -*- coding: utf-8 -*-
# Github: @felipsandoval
# para ejecutar: python3 -m unittest <nombre del fichero test_XXX.py>
# con el metodo de main se puede ejecutar como python3 <nombre del fichero test_XXX.py>
# python -m unittest discover -- 
# esto ejecutará TODOS los ficheros cuyo nombre empiecen por test y los ejecutará

from program import *
import unittest
#probar con type
class TestProgram(unittest.TestCase):
    def test_obtaining_json(self):
        self.assertEqual(obtaining_json("project.json"), json.loads(open("project.json").read()))
        self.assertEqual(obtaining_json("project.json"), json.loads(open("project.json").read()))

#unittest.main(argv=[''],verbosity=2, exit=False)

if __name__ == "__main__":
    unittest.main()