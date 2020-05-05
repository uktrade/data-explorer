#!/bin/bash

source ./scripts/functions.sh

run "npm install"
run "npm run-script build"
run "node -v"
run "python manage.py compilescss --delete-files"
run "python manage.py compilescss"
run "python manage.py collectstatic --ignore=*.scss --ignore=*.sass --ignore=package.json --ignore=package-lock.json --noinput"
