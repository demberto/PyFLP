from pyflp import Project


def test_patterns(project: Project):
    assert len(project.patterns) == 4
    assert project.patterns.current == project.patterns[4]
    assert project.patterns.play_cut_notes
    assert project.channels.swing == 64
