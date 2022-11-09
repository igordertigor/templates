#!/bin/bash

set -xe

{% if cookiecutter.git_init.lower().startswith("y") %}
git init
{% endif %}

{% if cookiecutter.create_venv.lower().startswith("y") %}
python3 -m venv .venv/
source .venv/bin/activate
pip install -r requirements.txt
{% endif %}
