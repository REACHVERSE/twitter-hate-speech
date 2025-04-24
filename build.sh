#!/usr/bin/env bash
# Exit on error
set -o errexit

project_root=$(pwd)

# Export the project root as an environment variable
export PROJECT_ROOT=$project_root

# Modify this line as needed for your package manager (pip, poetry, etc.)
pip install -r requirements.txt

#downloading bltk stopwords and punkt
# python -c "import nltk; nltk.download('stopwords')"
# python -c "import nltk; nltk.download('punkt')"
# python -c "import nltk; nltk.download('wordnet')"
python -m nltk.downloader stopwords punkt wordnet

# Convert static asset files
python manage.py collectstatic --no-input

# Apply any outstanding database migrations
python manage.py migrate

