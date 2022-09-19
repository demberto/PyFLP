import pathlib

import pytest

from pyflp import Project, parse
from pyflp.mixer import Mixer


@pytest.fixture(scope="session")
def project():
    return parse(pathlib.Path(__file__).parent / "assets" / "FL 20.8.4.flp")


@pytest.fixture(scope="session")
def arrangements(project: Project):
    return project.arrangements


@pytest.fixture(scope="session")
def rack(project: Project):
    return project.channels


@pytest.fixture(scope="session")
def mixer(project: Project):
    return project.mixer


@pytest.fixture(scope="session")
def inserts(mixer: Mixer):
    return tuple(mixer)[:25]


@pytest.fixture(scope="session")
def patterns(project: Project):
    return project.patterns
