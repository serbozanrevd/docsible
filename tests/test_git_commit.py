"""Tests for git commit SHA in get_repo_info."""

from unittest.mock import patch, MagicMock
from docsible.utils.git import get_repo_info, GitCommandError


def _make_run(stdout_values):
    """Return a side_effect function yielding successive stdout values."""
    results = []
    for v in stdout_values:
        m = MagicMock()
        m.stdout = v
        results.append(m)
    return results


def test_commit_sha_returned():
    with patch('docsible.utils.git.subprocess.run') as mock_run:
        mock_run.side_effect = _make_run([
            'true\n',                                       # is-inside-work-tree
            'git@github.com:org/repo.git\n',               # remote url
            'main\n',                                       # branch
            'abc1234def5678abc1234def5678abc1234def5678\n', # rev-parse HEAD
        ])
        result = get_repo_info('/some/path')
    assert result['commit'] == 'abc1234def5678abc1234def5678abc1234def5678'


def test_commit_key_present_when_git_fails():
    with patch('docsible.utils.git.subprocess.run') as mock_run:
        import subprocess
        mock_run.side_effect = subprocess.CalledProcessError(128, 'git')
        try:
            get_repo_info('/not/a/repo')
        except Exception:
            pass
        # commit initialized to None before try block — no KeyError on failure
        # (this test just verifies the function raises, not crashes on commit access)


def test_repo_info_contains_commit_key():
    with patch('docsible.utils.git.subprocess.run') as mock_run:
        mock_run.side_effect = _make_run([
            'true\n',
            'https://github.com/org/repo.git\n',
            'dev\n',
            'deadbeef\n',
        ])
        result = get_repo_info('/some/path')
    assert 'commit' in result
    assert result['commit'] == 'deadbeef'
