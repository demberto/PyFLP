import pytest

from pyflp._flobject import _FLObject


def test_invalid_ppq():
    with pytest.raises(ValueError):
        _FLObject._ppq = 0
        # TODO _FLObject().ppq = 0
