import pathlib

from pyflp import Parser


class NoFLPToTest(Exception):
    """No FLPs were found to run the test on"""


def test_nulltest():
    """Parse and save an FLP stream for every .flp
    file in 'assets' subfolders, compare for equality."""

    flps = tuple(pathlib.Path("tests/assets").glob("**/*.flp"))
    if not flps:
        raise NoFLPToTest()
    for flp in flps:
        original = open(flp, "rb").read()
        project = Parser(verbose=True).parse(original)
        new = project.get_stream()
        result = original == new
        assert result
