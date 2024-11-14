#!/usr/bin/env python
import os
import re

commandline_entrypoint = "{{ cookiecutter.commandline_entrypoint }}"
package_name = "{{ cookiecutter.package_name }}".strip('/')

if '=' in commandline_entrypoint:
    command, commandline_entrypoint = commandline_entrypoint.split('=')
else:
    command = package_name
command = command.strip()

entry_script, entry_func = commandline_entrypoint.strip().split(':')

if entry_script.startswith(package_name):
    entry_script = entry_script[len(package_name)+1:]

cleaned_entrypoint = f'{command} = {package_name}.{entry_script}:{entry_func}'

if entry_script.startswith('.'):
    entry_script = entry_script.replace('.', '/')

if entry_script.startswith('/'):
    entry_script = entry_script[1:]

if len(entry_script) == 0:
    fname = os.path.join('src', package_name, '__main__.py')
else:
    if not entry_script.endswith('.py'):
        entry_script = entry_script + '.py'

    fname = os.path.join('src', package_name, entry_script)

with open(fname, 'w') as f:
    f.write('\n'.join([
        '#!/usr/bin/env python',
        'import typer',
        '',
        'def main():',
        '    print("Hello world!")',
        '',
        f'def {entry_func}():',
        '    typer.run(main)',
    ]))


with open('setup.cfg') as f:
    txt = f.read()

with open('setup.cfg', 'w') as f:
    f.write(re.sub(
        r'__post_hook.commandline_entrypoint__',
        cleaned_entrypoint,
        txt,
    ))
