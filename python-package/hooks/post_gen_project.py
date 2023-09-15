#!/usr/bin/env python
from typing import Tuple, Optional
import os
import re
from dataclasses import dataclass, replace

# Pattern for entrypoints
# (command_name) =? callable
# If command_name is omitted, it will be the package name
# callable can be specified in two ways:
# 1. Filename:function
# 2. module:function
# where function will be `app` if omitted


PACKAGE_NAME = '{{ cookiecutter.package_name }}'


@dataclass
class Spec:
    func: str
    module: str
    command: str = 'app'
    filename: str = ''

    @property
    def qualifier(self) -> str:
        return f'{self.command} = {self.module}:{self.func}'


def format_entrypoint(entrypoint: str) -> Spec:
    if '=' in entrypoint:
        command, entrypoint = entrypoint.split('=')
    else:
        command = PACKAGE_NAME
    spec = sanitize(entrypoint.strip())
    return replace(
        spec, filename=get_filename(entrypoint), command=command.strip()
    )


def get_filename(spec: str) -> str:
    if ':' in spec:
        spec, _ = spec.split(':')
    if not spec.endswith('.py'):
        filename = spec.replace('.', '/')
    if os.path.basename(filename) == PACKAGE_NAME:
        filename = os.path.join(filename, '__init__')
    if not filename.startswith('src/'):
        filename = os.path.join('src', filename)
    return filename + '.py'


def sanitize(spec: str) -> Spec:
    if ':' in spec:
        qualifier, func = spec.split(':')
    else:
        qualifier = spec
        func = 'app'
    return Spec(func=func, module=maybe_convert_filename(qualifier))


def maybe_convert_filename(filename_or_module: str) -> str:
    if filename_or_module.endswith('.py'):
        return convert_filename(filename_or_module)
    else:
        return filename_or_module


def convert_filename(filename: str) -> str:
    if filename.startswith('src/'):
        filename = filename[4:]
    filename = filename[:-3]  # drop trailing '.py'
    return filename.replace('/', '.')


spec = format_entrypoint(
    '{{ cookiecutter.commandline_entrypoint }}'
)

with open(spec.filename, 'w') as f:
    f.write(
        '\n'.join(
            [
                '#!/usr/bin/env python',
                '"""',
                'Usage:',
                f'    { spec.command } [options]',
                '',
                'Options:',
                '"""',
                '',
                'from docopt import docopt',
                '',
                f'def { spec.func }():',
                '    args = docopt(__doc__)',
            ]
        )
    )


with open('pyproject.toml') as f:
    txt = f.read()

with open('pyproject.toml', 'w') as f:
    f.write(
        re.sub(
            r'__post_hook.commandline_entrypoint__',
            spec.qualifier,
            txt,
        )
    )
