from __future__ import annotations

import pathlib

import pytest

import construct
import pyflp

CORRUPTED = pathlib.Path(__file__).parent / "assets" / "corrupted"


def test_invalid_header_magic():
    with pytest.raises(construct.ConstError):
        pyflp.parse(CORRUPTED / "invalid-header-magic.flp")


def test_invalid_header_size():
    with pytest.raises(construct.ConstError):
        pyflp.parse(CORRUPTED / "invalid-header-size.flp")


def test_invalid_format():
    with pytest.raises(ValueError, match="256"):
        pyflp.parse(CORRUPTED / "invalid-format.flp")


def test_invalid_ppq():
    with pytest.raises(construct.ValidationError):
        # ! Opening this FLP in FL will crash it with a division by zero error
        pyflp.parse(CORRUPTED / "invalid-ppq.flp")


def test_invalid_data_magic():
    with pytest.raises(construct.ConstError):
        pyflp.parse(CORRUPTED / "invalid-data-magic.flp")
