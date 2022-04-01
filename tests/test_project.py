"""Tests `pyflp.project.Project` class."""

from pyflp import Project


def test_utilities(proj: Project, tmp_path):
    """Tests certain utility functions and project saving."""
    assert proj.used_insert_nums() == set((0, 1, 5, 6))
    assert proj.slots_used() == 6
    proj.save(tmp_path / "new.flp")
