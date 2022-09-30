from __future__ import annotations

import pathlib

import pytest

import pyflp
from pyflp import HeaderCorrupted

CORRUPTED = pathlib.Path(__file__).parent / "assets" / "corrupted"


def test_invalid_header_magic():
    with pytest.raises(HeaderCorrupted, match="FLhd"):
        pyflp.parse(CORRUPTED / "invalid-header-magic.flp")


def test_invalid_header_size():
    with pytest.raises(HeaderCorrupted, match="6"):
        pyflp.parse(CORRUPTED / "invalid-header-size.flp")


def test_invalid_format():
    with pytest.raises(HeaderCorrupted, match="Unsupported project file format"):
        pyflp.parse(CORRUPTED / "invalid-format.flp")


def test_invalid_ppq():
    with pytest.raises(HeaderCorrupted, match="Invalid PPQ"):
        # ! Opening this FLP in FL will crash it with a division by zero error
        pyflp.parse(CORRUPTED / "invalid-ppq.flp")


def test_invalid_data_magic():
    with pytest.raises(HeaderCorrupted, match="FLdt"):
        pyflp.parse(CORRUPTED / "invalid-data-magic.flp")


def test_invalid_data_size():
    with pytest.raises(HeaderCorrupted, match="Data chunk size corrupted"):
        pyflp.parse(CORRUPTED / "invalid-event-size.flp")
