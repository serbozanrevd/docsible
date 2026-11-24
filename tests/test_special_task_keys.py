"""Tests for process_special_task_keys enriched task fields."""

from docsible.utils.special_tasks_keys import process_special_task_keys


def test_basic_fields_present():
    task = {'name': 'Install curl', 'ansible.builtin.apt': {'name': 'curl'}}
    result = process_special_task_keys(task)
    assert len(result) == 1
    t = result[0]
    assert t['name'] == 'Install curl'
    assert t['module'] == 'ansible.builtin.apt'
    assert t['args'] == {'name': 'curl'}
    assert t['when'] is None
    assert t['failed_when'] is None
    assert t['register'] is None
    assert t['notify'] == []
    assert t['vars'] == {}


def test_failed_when_captured():
    task = {'name': 'Run cmd', 'ansible.builtin.command': 'ls', 'failed_when': 'rc != 0'}
    result = process_special_task_keys(task)
    assert result[0]['failed_when'] == 'rc != 0'


def test_register_captured():
    task = {'name': 'Run cmd', 'ansible.builtin.command': 'ls', 'register': 'cmd_result'}
    result = process_special_task_keys(task)
    assert result[0]['register'] == 'cmd_result'


def test_notify_string_normalized_to_list():
    task = {'name': 'Install pkg', 'ansible.builtin.apt': {'name': 'nginx'}, 'notify': 'restart nginx'}
    result = process_special_task_keys(task)
    assert result[0]['notify'] == ['restart nginx']


def test_notify_list_preserved():
    task = {'name': 'Install pkg', 'ansible.builtin.apt': {'name': 'nginx'}, 'notify': ['restart nginx', 'reload config']}
    result = process_special_task_keys(task)
    assert result[0]['notify'] == ['restart nginx', 'reload config']


def test_vars_captured():
    task = {'name': 'Set fact', 'ansible.builtin.set_fact': {'foo': 'bar'}, 'vars': {'local_var': 1}}
    result = process_special_task_keys(task)
    assert result[0]['vars'] == {'local_var': 1}


def test_meta_flush_handlers():
    task = {'meta': 'flush_handlers'}
    result = process_special_task_keys(task)
    assert result[0]['module'] == 'flush_handlers'


def test_when_list_escaped():
    task = {'name': 'Conditional', 'ansible.builtin.debug': {'msg': 'hi'}, 'when': ['cond1', 'cond2|something']}
    result = process_special_task_keys(task)
    assert result[0]['when'] == ['cond1', 'cond2¦something']


def test_block_tasks_still_work():
    task = {
        'name': 'My block',
        'block': [
            {'name': 'Inner task', 'ansible.builtin.debug': {'msg': 'hi'}}
        ]
    }
    result = process_special_task_keys(task)
    assert result[0]['module'] == 'block'
    assert result[1]['module'] == 'ansible.builtin.debug'


def test_block_entry_has_all_fields():
    task = {'block': [{'name': 'x', 'ansible.builtin.debug': {'msg': 'hi'}}]}
    result = process_special_task_keys(task)
    block = result[0]
    assert block['failed_when'] is None
    assert block['args'] == {}
    assert block['vars'] == {}
    assert block['notify'] == []
    assert block['register'] is None
