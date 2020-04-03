#!/bin/bash

source ./scripts/functions.sh

run "python manage.py migrate --noinput"
run "python manage.py collectstatic --noinput"


if [[ -z "${DEVELOPMENT_SERVER}" ]]; then
    run "waitress-serve --port=$PORT data_explorer.wsgi:application"
fi