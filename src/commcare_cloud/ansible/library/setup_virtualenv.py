#! /usr/bin/env python3
from __future__ import (absolute_import, division, print_function)

from pathlib import Path
from shlex import quote

from ansible.module_utils.basic import AnsibleModule

__metaclass__ = type


DOCUMENTATION = """
---
module: setup_virtualenv

short_description: Setup virtualenv for a software release.

version_added: "1.0.0"

description: Create a virtualenv for a software release. Use
    'virtualenv-clone' to copy the virtualenv from a previous release
    as a starting point. Then update requirements with 'pip-sync'.

options:
    src:
        description: Directory path containing a previous release.
        required: true
        type: str
    dest:
        description: Directory path in which to create the new virtualenv.
        required: true
        type: str
    env_name:
        description: Virtualenv base name. The python version is added
            to the virtualenv name, and a symlink is created linking the
            base name to the virtualenv directory. Default: 'python_env'
        required: false
        default: 'python_env'
        type: str
    python_version:
        description: Python version.
        required: true
        type: str
    requirements_file:
        description: Pip requirements file path (may be relative to dest).
        required: true
        type: str
    http_proxy:
        description: HTTP proxy address.
        required: false
        type: str

extends_documentation_fragment:
    - commcare_cloud.ansible

author:
    - Daniel Miller (@millerdev)
"""

EXAMPLES = """
- name: Setup virtualenv
  setup_virtualenv:
    src: "/path/to/releases/previous"
    dest: "/path/to/releases/next"
    python_version: "3.9"
    requirements_file: "requirements/prod-requirements.txt"
"""

RETURN = """
changed:
    description: Changed flag.
    type: bool
diff:
    description: Dict of before and after states of the virtualenv.
    type: dict
    sample: {'before': {'path': ...}, 'after': {'path': ...}}
venv:
    description: Path of the new virtualenv.
    type: str
    sample: /path/to/releases/next/python_env
"""


def main():
    module_args = {
        'src': {'type': 'str', 'required': True},
        'dest': {'type': 'str', 'required': True},
        'env_name': {'type': 'str', 'default': 'python_env'},
        'python_version': {'type': 'str', 'required': True},
        'requirements_file': {'type': 'str', 'required': True},
        'http_proxy': {'type': 'str', 'default': None},
    }
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )
    params = module.params
    env_name = params["env_name"]
    python_version = params["python_version"]
    full_env_name = f"{env_name}-{python_version}"
    src = Path(params["src"])
    dest = Path(params["dest"])
    # resolve() because of bug in virtualenv-clone: can't clone env from symlink
    prev_env = src.resolve() / full_env_name
    next_env = dest / full_env_name
    python_env = dest / env_name
    requirements_file = dest / params["requirements_file"]
    proxy = params["http_proxy"]

    diff = {'before': {'path': str(prev_env)}, 'after': {'path': str(next_env)}}
    result = {'changed': False, 'venv': str(python_env), 'diff': diff}

    if not python_env.exists():
        result["changed"] = True
        if not module.check_mode:
            if not (next_env / "bin/python").exists():
                if not prev_env.exists():
                    module.fail_json(msg=f"virtualenv not found: {prev_env}")
                    return
                clone_virtualenv(prev_env, next_env, module)
            pip_sync(requirements_file, next_env, module, proxy)
            python_env.symlink_to(full_env_name)

    module.exit_json(**result)


def clone_virtualenv(prev_env, next_env, module):
    module.run_command(["virtualenv-clone", prev_env, next_env], check_rc=True)


def pip_sync(requirements_file, venv_path, module, proxy):
    pip = venv_path / "bin/pip"
    pip_args = ["--timeout=60"]
    if proxy:
        pip_args.append(f"--proxy={quote(proxy)}")
    module.run_command(
        [pip, "install", "--quiet", "--upgrade", *pip_args, "pip-tools"],
        check_rc=True,
    )
    pip_sync = venv_path / "bin/pip-sync"
    module.run_command(
        [pip_sync, "--quiet", f"--pip-args={' '.join(pip_args)}", requirements_file],
        check_rc=True,
    )


class Error(Exception):
    pass


if __name__ == '__main__':
    main()
