#!/bin/bash

python -m pip install -r requirements.txt

cd eave_django_playground/
# python manage.py makemigrations
python manage.py migrate
