from pyflp import Parser

def test_nulltest():
    """Parse and save an FLP stream for every .flp file in 'assets' folder, compare for equality."""
    
    original = open("tests/assets/FL 20.8.3.2304 Empty.flp", 'rb').read()
    project = Parser(verbose=True).parse(original)
    new = project.get_stream()
    assert original == new