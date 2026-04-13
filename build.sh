#!/usr/bin/env bash
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Collect static files from the Django project
python api_test_server/manage.py collectstatic --noinput

# Run migrations from the Django project directory
python api_test_server/manage.py migrate
