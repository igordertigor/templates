#!/bin/bash

set -xe

BACKUP_SETUP=$(mktemp)
NEW_SETUP=$(mktemp)

cp setup.cfg $BACKUP_SETUP

function cleanup() {
  mv $BACKUP_SETUP setup.cfg
  rm $NEW_SETUP
}

track cleanup ERR

# bump version
sed -r 's/version = ([0-9]+)/echo version = $((\1+1))"/e' setup.cfg > $NEW_SETUP
mv $NEW_SETUP setup.cfg

VERSION=$(awk '/version = [0-9]+/ { print $3 }' setup.cfg)

SOURCEDIST={{ cookiecutter.package_name }}-${VERSION}.tar.gz
BINDIST=csvmodel-${VERSION}-py3-name-any.whl

{% if cookiecutter.commandline_entrypoint %}
cram README.md
{% endif %}

python -m build

twine check dist/$SOURCEDIST dist/$BINDIST
twine upload --verbose dist/$SOURCEDIST dist/$BINDIST

echo "****************************************************"
echo "* Now commit setup.cfg and tag the commit as v${VERSION}"
echo "****************************************************"

rm $BACKUP_SETUP
