# Data Explorer

Small django application to demo django-sql-explorer

Steps to run locally
 - `cp envs/sample.env .env`
 - `docker-compose up --build`
 
To use the django development server add the following setting to `.env`
 - `DEVELOPMENT_SERVER=1` 
 - `docker exec -ti data_explorer_1 /bin/bash`
 - `/manage.py runserver_plus 0.0.0.0:8000`
 
To run tests locally (excludes functional tests):
 - `pip install -r requirements-dev.txt`
 - `make run_tests`
 
To run functional tests locally:
 - Install chrome/chromium and chromedriver; make sure both are available in PATH.
 - `pip install -r requirements-dev.txt`
 - `pytest explorer/tests/functional`

To run all tests in docker:
 - `make docker-test`
