"""Tests for task file ordering: main.yml first, rest alphabetical."""

from unittest.mock import patch
from docsible.cli import document_role


def _make_role(tmp_path):
    tasks = tmp_path / "tasks"
    tasks.mkdir()
    (tasks / "main.yml").write_text("- name: Main task\n  ansible.builtin.debug:\n    msg: main\n")
    (tasks / "configure.yml").write_text("- name: Configure\n  ansible.builtin.debug:\n    msg: configure\n")
    (tasks / "install.yml").write_text("- name: Install\n  ansible.builtin.debug:\n    msg: install\n")
    (tmp_path / "meta").mkdir()
    (tmp_path / "meta" / "main.yml").write_text("galaxy_info:\n  author: test\n")
    return str(tmp_path)


def test_main_yml_is_first(tmp_path):
    role_path = _make_role(tmp_path)
    output = str(tmp_path / "README.md")
    with patch('docsible.cli.get_repo_info', side_effect=Exception("no git")):
        role_info = document_role(
            role_path, None, False, True, True, False, False,
            None, False, False, output,
            None, None, None,
        )
    files = [t['file'] for t in role_info['tasks']]
    assert files[0] == 'main.yml'


def test_remaining_files_sorted_alphabetically(tmp_path):
    role_path = _make_role(tmp_path)
    output = str(tmp_path / "README.md")
    with patch('docsible.cli.get_repo_info', side_effect=Exception("no git")):
        role_info = document_role(
            role_path, None, False, True, True, False, False,
            None, False, False, output,
            None, None, None,
        )
    files = [t['file'] for t in role_info['tasks']]
    assert files == ['main.yml', 'configure.yml', 'install.yml']
