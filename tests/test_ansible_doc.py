"""Tests for --ansible_doc flag loading."""

import json
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

from docsible.cli import document_role


def _make_role(tmp_path):
    """Create a minimal valid role structure."""
    (tmp_path / "tasks").mkdir()
    (tmp_path / "tasks" / "main.yml").write_text("- name: Test\n  ansible.builtin.debug:\n    msg: hi\n")
    (tmp_path / "meta").mkdir()
    (tmp_path / "meta" / "main.yml").write_text("galaxy_info:\n  author: test\n")
    return str(tmp_path)


def test_ansible_doc_loaded_into_role_info(tmp_path):
    role_path = _make_role(tmp_path)
    doc_file = tmp_path / "ansible_verbiage.json"
    doc_file.write_text(json.dumps({"ansible.builtin.debug": "Print statements during execution."}))

    output = str(tmp_path / "README.md")
    with patch('docsible.cli.get_repo_info', side_effect=Exception("no git")):
        role_info = document_role(
            role_path, None, False, True, True, False, False,
            None, False, False, output,
            None, None, None,
            ansible_doc=str(doc_file)
        )

    assert role_info["ansible_doc"] == {"ansible.builtin.debug": "Print statements during execution."}


def test_ansible_doc_missing_file_aborts(tmp_path, capsys):
    """document_role should not crash when ansible_doc path is invalid — CLI guards this."""
    # The CLI guard (early return) is in doc_the_role; document_role itself will
    # raise FileNotFoundError if path is wrong. Verify that behaviour is explicit.
    role_path = _make_role(tmp_path)
    output = str(tmp_path / "README.md")
    try:
        with patch('docsible.cli.get_repo_info', side_effect=Exception("no git")):
            document_role(
                role_path, None, False, True, True, False, False,
                None, False, False, output,
                None, None, None,
                ansible_doc="/nonexistent/path.json"
            )
        assert False, "Expected FileNotFoundError"
    except FileNotFoundError:
        pass


def test_ansible_doc_empty_when_not_provided(tmp_path):
    role_path = _make_role(tmp_path)
    output = str(tmp_path / "README.md")
    with patch('docsible.cli.get_repo_info', side_effect=Exception("no git")):
        role_info = document_role(
            role_path, None, False, True, True, False, False,
            None, False, False, output,
            None, None, None,
        )
    assert role_info["ansible_doc"] == {}
