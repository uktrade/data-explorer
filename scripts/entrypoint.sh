#!/bin/bash

source ./scripts/functions.sh


# run the scheduled task to populate the database in the celery app
run "python manage.py migrate --noinput"

if [[ -z "${DEVELOPMENT_SERVER}" ]]; then
    run "waitress-serve --port=$PORT config.wsgi:application"
fi