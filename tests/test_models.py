from __future__ import annotations

from pyflp._models import FLVersion


def test_flversion():
    assert str(FLVersion(20, 8, 4)) == "20.8.4"
    assert str(FLVersion(20, 8, 4, 2576)) == "20.8.4.2576"
