from __future__ import annotations

import itertools
import pathlib
import sys
from typing import TypeVar

if sys.version_info >= (3, 8):
    from typing import Protocol
else:
    from typing_extensions import Protocol

import pytest

import pyflp
from pyflp import Project
from pyflp._events import EventEnum
from pyflp._models import ModelBase
from pyflp.mixer import Mixer

T = TypeVar("T", bound=ModelBase)


class ModelFixture(Protocol):
    def __call__(self, suffix: str, type: type[T], *only: EventEnum) -> T:
        ...


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


@pytest.fixture
def get_model():
    def wrapper(suffix: str, type: type[ModelBase], *only: EventEnum):
        parsed = pyflp.parse(pathlib.Path(__file__).parent / "assets" / suffix)
        if only:
            events = [v for k, v in parsed.events_asdict().items() if k in only]
            return type(*itertools.chain.from_iterable(events))
        return type(*parsed.events_astuple())

    return wrapper
