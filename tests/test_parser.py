"""This doesn't work yet :("""

import unittest
from pyflp.parser import ProjectParser

class TestParser(unittest.TestCase):
    def null_test(self) -> bool:
        '''Parse and save an FLP stream, compare for equality'''
        original = open("assets/FL 20.8.3.2304/Empty.flp", 'rb').read()
        project = ProjectParser(verbose=True).parse(original)
        new = project.get_stream()
        return original == new