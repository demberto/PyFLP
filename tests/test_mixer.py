from pyflp import Project


def test_mixer(project: Project):
    assert len(project.mixer) == 127
