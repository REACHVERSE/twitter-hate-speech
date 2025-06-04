#!/usr/bin/env bash
set -o errexit

project_root=$(pwd)
export PROJECT_ROOT=$project_root

pip install -r requirements.txt

# Removed nltk download step

python manage.py collectstatic --no-input
python manage.py migrate
