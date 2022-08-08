#!/bin/bash

pushd "explore-{{ cookiecutter.repo_name_suffix }}/"

{% if cookiecutter.git_init %}
git init
{% endif %}

{% if cookiecutter.create_venv %}
python3 -m venv .venv/
source .venv/bin/activate
pip install -r requirements.txt
{% endif %}

popd
