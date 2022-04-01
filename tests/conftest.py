import os
import zipfile

import pytest

from pyflp import Parser, Project

curdir = os.path.dirname(__file__)


@pytest.fixture(scope="session")
def proj() -> Project:
    with zipfile.ZipFile(f"{curdir}/assets/FL 20.8.3.zip") as zp:
        return Parser().parse_zip(zp)
