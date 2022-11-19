from __future__ import annotations

import pathlib
from typing import TypeVar

import pytest

import pyflp
from pyflp import Project
from pyflp._events import EventEnum
from pyflp._models import ModelBase
from pyflp.mixer import Mixer

MT = TypeVar("MT", bound=ModelBase)


@pytest.fixture(scope="session")
def project():
    return pyflp.parse(pathlib.Path(__file__).parent / "assets" / "FL 20.8.4.flp")


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


def get_model(suffix: str, type: type[MT], *only: EventEnum) -> MT:
    parsed = pyflp.parse(pathlib.Path(__file__).parent / "assets" / suffix)
    if only:
        return type(parsed.events.subtree(lambda e: e.id in only))
    return type(parsed.events)
