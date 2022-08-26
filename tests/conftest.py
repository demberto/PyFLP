import pathlib

import pytest

import pyflp


@pytest.fixture(scope="session")
def project():
    return pyflp.parse(pathlib.Path(__file__).parent / "assets" / "FL 20.8.3.flp")
