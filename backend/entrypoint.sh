#!/bin/sh

sleep 3


poetry run python backend/manage.py migrate
poetry run python backend/manage.py runserver 0.0.0.0:8000
