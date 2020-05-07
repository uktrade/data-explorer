#!/bin/bash

source ./scripts/functions.sh

run "./scripts/compile_assets.sh"
run "./scripts/compile_sass.sh"

run "python manage.py migrate --noinput"
run "waitress-serve --port=$PORT data_explorer.wsgi:application"
