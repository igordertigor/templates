#!/bin/bash

set -xe

python3 -m venv .venv
source .venv/bin/activate
pip install jinja2 'watchdog[watchmedo]'
