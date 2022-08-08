#!/usr/bin/env python
import os

commandline_entrypoint = "{{ cookiecutter.commandline_entrypoint }}"
package_name = "{{ cookiecutter.package_name }}".strip('/')

commandline_entrypoint = commandline_entrypoint.split('=')[-1].strip()
entry_script, entry_func = commandline_entrypoint.split(':')


if entry_script.startswith(package_name):
    entry_script = entry_script[len(package_name):]
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
        '"""',
        'Usage:',
        '    {{ cookiecutter.commandline_entrypoint }} [options]',
        '',
        'Options:',
        '"""',
        '',
        'from docopt import docopt',
        '',
        f'def {entry_func}():',
        '    args = docopt(__doc__)',
    ]))
