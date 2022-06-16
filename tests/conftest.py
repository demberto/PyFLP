# PyFLP - An FL Studio project file (.flp) parser
# Copyright (C) 2022 demberto
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option)
# any later version. This program is distributed in the hope that it will be
# useful, but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General
# Public License for more details. You should have received a copy of the
# GNU General Public License along with this program. If not, see
# <https://www.gnu.org/licenses/>.

import os
import zipfile

import pytest

from pyflp import Parser, Project
from pyflp._event import (
    ByteEventType,
    ColorEventType,
    DataEventType,
    DWordEventType,
    EventList,
    EventType,
    TextEventType,
    WordEventType,
    _ByteEvent,
    _ColorEvent,
    _DataEvent,
    _DWordEvent,
    _TextEvent,
    _WordEvent,
)

curdir = os.path.dirname(__file__)
eventlist = EventList()


@pytest.fixture(scope="session")
def proj() -> Project:
    with zipfile.ZipFile(f"{curdir}/assets/FL 20.8.3.zip") as zp:
        return Parser().parse_zip(zp)


# Pass a parameter to a fixture function: https://stackoverflow.com/a/68286553
@pytest.fixture
def event() -> EventType:
    def _event(typ, id_, data, *args):
        return eventlist.create(typ, id_, data, *args)

    yield _event


@pytest.fixture
def byteevent(event) -> ByteEventType:
    def _byteevent(id_, data):
        return event(_ByteEvent, id_, data)

    yield _byteevent


@pytest.fixture
def wordevent(event) -> WordEventType:
    def _wordevent(id_, data):
        return event(_WordEvent, id_, data)

    yield _wordevent


@pytest.fixture
def dwordevent(event) -> DWordEventType:
    def _dwordevent(id_, data):
        return event(_DWordEvent, id_, data)

    yield _dwordevent


@pytest.fixture
def colorevent(event) -> ColorEventType:
    def _colorevent(id_, data):
        return event(_ColorEvent, id_, data)

    yield _colorevent


@pytest.fixture
def textevent(event) -> TextEventType:
    def _textevent(id_, data, uses_unicode):
        return event(_TextEvent, id_, data, uses_unicode)

    yield _textevent


@pytest.fixture
def dataevent(event) -> DataEventType:
    def _dataevent(id_, data):
        return event(_DataEvent, id_, data)

    yield _dataevent
