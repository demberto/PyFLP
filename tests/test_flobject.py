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

import pytest

from pyflp._flobject import _FLObject, _MaxInstancedFLObject
from pyflp.exceptions import MaxInstancesError


def test_invalid_ppq():
    with pytest.raises(ValueError):
        _FLObject._ppq = 0
        # TODO _FLObject().ppq = 0


def test_max_instances(monkeypatch):
    monkeypatch.setattr(_MaxInstancedFLObject, "max_count", -1)
    with pytest.raises(MaxInstancesError):
        _MaxInstancedFLObject()
