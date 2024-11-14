#!/bin/bash

set -xe

{% if cookiecutter.increment_version_on_publish %}
VERSION=$(semv)
git tag $VERSION
{% else %}
VERSION=$(python -c 'from setuptools_scm import get_version; print(get_version())')
{% endif %}

SOURCEDIST={{ cookiecutter.package_name }}-${VERSION}.tar.gz
BINDIST={{ cookiecutter.package_name }}-${VERSION}-py3-name-any.whl

{% if cookiecutter.commandline_entrypoint %}
cram README.md
{% endif %}

python -m build

twine check dist/$SOURCEDIST dist/$BINDIST
twine upload --verbose dist/$SOURCEDIST dist/$BINDIST
