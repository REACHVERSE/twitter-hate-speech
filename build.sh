#!/usr/bin/env bash
# Exit on error
set -o errexit

project_root=$(pwd)

# Export the project root as an environment variable
export PROJECT_ROOT=$project_root

# Modify this line as needed for your package manager (pip, poetry, etc.)
pip install -r requirements.txt

#downloading bltk stopwords and punkt
python -m nltk.downloader punkt wordnet stopwords

# Convert static asset files
python manage.py collectstatic --no-input

# Apply any outstanding database migrations
python manage.py migrate

