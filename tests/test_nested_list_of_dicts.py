from docsible.markdown_template import static_template
from jinja2 import Environment, BaseLoader
import yaml
from pathlib import Path
from docsible.cli import type_debug, to_yaml

FIXTURES = Path(__file__).parent / "fixtures"

def load_fixture(name):
  with open(FIXTURES / name) as f:
      return yaml.safe_load(f)

def render_template(argument_specs):

  env = Environment(loader=BaseLoader)
  env.filters['type_debug'] = type_debug
  env.filters['to_yaml'] = to_yaml

  role_info = {
      "name": "test_role",
      "argument_specs": argument_specs,
      "defaults": [],
      "vars": [],
      "tasks": [],
      "meta": {},
      "playbook": {"content": None, "graph": None},
      "docsible": None,
      "belongs_to_collection": False,
      "repository": None,
      "repository_type": None,
      "repository_branch": None,
      "repo_commit": None,
      "ansible_doc": {},
  }

  template = env.from_string(static_template)
  return template.render(
      role=role_info,
      mermaid_code_per_file={},
  )


def test_nested_list_of_dicts_without_default():
  rendered = render_template(
      load_fixture("minimal_arg_specs.yml")
  )
  # my_list is rendered; nested options not shown without a populated default
  assert "**my_list**" in rendered
  assert "Type**: list" in rendered

def test_nested_list_of_dicts_with_default():
  rendered = render_template(
      load_fixture("minimal_arg_specs_with_default.yml")
  )
  assert "**my_list**" in rendered
  # nested items rendered via default entries (indented with 4 spaces)
  assert "    - **name**" in rendered
  assert rendered.index("my_list") < rendered.index("name")
