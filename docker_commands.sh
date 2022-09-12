#!/bin/sh

# shellcheck disable=SC2164
cd backend

python3 manage.py makemigrations
python3 manage.py migrate --fake sessions zero
python3 manage.py showmigrations
python3 manage.py migrate --fake-initial
python3 manage.py collectstatic --noinput
python3 manage.py create_admin
#python3 manage.py runserver 0.0.0.0:8000
gunicorn backend.asgi:application -k uvicorn.workers.UvicornWorker