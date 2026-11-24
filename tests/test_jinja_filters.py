"""Tests for type_debug and to_yaml Jinja2 filters."""

import yaml
from docsible.cli import type_debug, to_yaml


def test_type_debug_str():
    assert type_debug("hello") == "str"


def test_type_debug_int():
    assert type_debug(42) == "int"


def test_type_debug_list():
    assert type_debug([]) == "list"


def test_type_debug_dict():
    assert type_debug({}) == "dict"


def test_type_debug_bool():
    assert type_debug(True) == "bool"


def test_to_yaml_produces_valid_yaml():
    data = {"key": "value", "count": 3}
    result = to_yaml(data)
    parsed = yaml.safe_load(result)
    assert parsed == data


def test_to_yaml_no_line_wrap():
    long_string = "x" * 200
    result = to_yaml({"key": long_string})
    # width=inf means no wrapping — value stays on one line
    assert "\n  " not in result
