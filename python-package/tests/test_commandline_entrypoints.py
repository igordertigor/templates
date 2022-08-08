from contextlib import contextmanager
import os
import re
import glob
from tempfile import TemporaryDirectory
from cookiecutter.main import cookiecutter


@contextmanager
def user_specifies(spec: str):
    TEMPLATE = os.path.join(
        os.path.dirname(__file__),
        '..',
    )
    with TemporaryDirectory() as tmpdir:
        cookiecutter(
            TEMPLATE,
            no_input=True,
            extra_context={'commandline_entrypoint': spec},
            output_dir=tmpdir,
        )
        yield tmpdir


def entry_in_setup(tmpdir: str) -> str:
    with open(os.path.join(tmpdir, 'mypackage/setup.cfg')) as f:
        m = re.search(
            r'console_scripts =\n\s+(.*)',
            f.read(),
        )
        return m.group(1)


def funcname_in_file(tmpdir: str, fname: str) -> str:
    with open(os.path.join(tmpdir, 'mypackage/src/', fname)) as f:
        m = re.search(
            r'def ([\w_]+)\(',
            f.read(),
        )
        return m.group(1)



def test_only_package_and_func():
    with user_specifies('cli:func') as tmpdir:
        assert entry_in_setup(tmpdir) == 'mypackage = mypackage.cli:func'
        assert funcname_in_file(tmpdir, 'mypackage/cli.py') == 'func'


def test_full_spec():
    with user_specifies('mypackage = mypackage.cli:func') as tmpdir:
        assert entry_in_setup(tmpdir) == 'mypackage = mypackage.cli:func'
        assert funcname_in_file(tmpdir, 'mypackage/cli.py') == 'func'


def test_full_spec_different_command():
    with user_specifies('some_command = mypackage.cli:func') as tmpdir:
        assert entry_in_setup(tmpdir) == 'some_command = mypackage.cli:func'
        assert funcname_in_file(tmpdir, 'mypackage/cli.py') == 'func'

def test_commandname_package_and_func():
    with user_specifies('some_command = cli:func') as tmpdir:
        assert entry_in_setup(tmpdir) == 'some_command = mypackage.cli:func'
        assert funcname_in_file(tmpdir, 'mypackage/cli.py') == 'func'
