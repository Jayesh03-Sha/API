#!/usr/bin/env bash
set -o errexit

export PORT=${PORT:-10000}
exec gunicorn api_test_server.api_test_server.wsgi:application --bind 0.0.0.0:$PORT
