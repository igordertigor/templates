# Template for python-package

This is a template for a python package with an optional additional
command line interface.

Features:
- `pyproject.toml` as main config file
- simple `tox.ini` setup with flake8, mypy, unit tests, integration tests, coverage, build/upload to pypi tasks
- `semv` for commit based semantic versioning
- templates for command line interfaces using [docopt](http://docopt.org) or [typer](https://typer.tiangolo.com).
