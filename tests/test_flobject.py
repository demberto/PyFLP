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
