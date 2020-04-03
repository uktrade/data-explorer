# Data Explorer

Small django application to demo django-sql-explorer

Steps to run locally
 - `cp envs/sample.env .env`
 - `docker-compose up --build`
 
To use the django development server add the following setting to `.env`
 - `DEVELOPMENT_SERVER=1` 
 - `docker exec -ti data_explorer_1 /bin/bash`
 - `/manage.py runserver_plus 0.0.0.0:8000`
 
A super user is required to access the explorer
 - `docker exec -ti data_explorer_1 /bin/bash`
 - `./manage.py createsuperuser` 
