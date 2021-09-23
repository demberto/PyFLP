import pathlib
from pyflp import Parser

def test_nulltest():
    """Parse and save an FLP stream for every .flp file in 'assets' folder, compare for equality."""
    
    for flp in tuple(pathlib.Path("tests/assets").glob(".flp")):
        original = open(flp, 'rb').read()
        project = Parser(verbose=True).parse(original)
        new = project.get_stream()
        assert original == new