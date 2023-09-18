#!/bin/bash

set xe

python -m http.server &
SERVER_PID=$!

trap 'kill $SERVER_PID' EXIT

watchmedo shell-command --patterns="*.md;*.css" --command='python render.py' .
