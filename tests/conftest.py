import pathlib

import pytest

import pyflp


@pytest.fixture(scope="session")
def project():
    return pyflp.parse(pathlib.Path(__file__).parent / "assets" / "FL 20.8.4.flp")


@pytest.fixture(scope="session")
def arrangements(project: pyflp.Project):
    return project.arrangements


@pytest.fixture(scope="session")
def rack(project: pyflp.Project):
    return project.channels


@pytest.fixture(scope="session")
def mixer(project: pyflp.Project):
    return project.mixer


@pytest.fixture(scope="session")
def patterns(project: pyflp.Project):
    return project.patterns
