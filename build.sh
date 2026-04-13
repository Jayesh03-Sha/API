#!/usr/bin/env bash
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Run migrations from the Django project directory
python api_test_server/manage.py migrate

# Collect static files
python api_test_server/manage.py collectstatic --no-input
