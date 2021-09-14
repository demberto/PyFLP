"""This doesn't work yet :("""

import unittest
import pathlib
from pyflp import Parser

class TestParser(unittest.TestCase):
    def null_test(self) -> bool:
        '''Parse and save an FLP stream for every .flp file in 'assets' folder, compare for equality.'''
        for flp in tuple(pathlib.Path("assets").glob(".flp")):
            original = open(flp, 'rb').read()
            project = Parser(verbose=True).parse(original)
            new = project.get_stream()
            return original == new