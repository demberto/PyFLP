"""Tests `pyflp.project.Project` class and property setters."""

import os
import random
import zipfile

import pytest

from pyflp import Project


@pytest.mark.order(index=0)
def test_nulltest(proj: Project):
    new = proj.get_stream()
    curdir = os.path.dirname(__file__)
    with zipfile.ZipFile(f"{curdir}/assets/FL 20.8.3.zip") as zp:
        original = zp.open("FL 20.8.3.flp").read()
    result = original == new
    assert result


def test_utilities(proj: Project):
    """Tests certain utility functions."""
    assert proj.used_insert_nums() == set((0, 1, 5, 6))
    assert proj.slots_used() == 7


@pytest.mark.order(index=-1)
def test_save(proj: Project, tmp_path):
    proj.save(tmp_path / "new.flp")


def test_misc(proj: Project):
    r = random.randint(0, 20)
    proj.misc.version = f"{r}.{r}.{r}"
    with pytest.raises(ValueError):
        proj.misc.version = "1.0"
