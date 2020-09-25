#!/bin/sh

/wait-for-it.sh db:5432 -t 300
python manage.py makemigrations
python manage.py migrate
gunicorn config.wsgi:application --bind 0.0.0.0:8000