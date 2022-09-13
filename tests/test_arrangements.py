from pyflp import Project


def test_arrangements(project: Project):
    assert len(project.arrangements) == 2
    assert project.arrangements.loop_pos is None
    assert project.arrangements.time_signature.num == 2
    assert project.arrangements.time_signature.beat == 8
