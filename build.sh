#!/usr/bin/env bash
# Exit on error
set -o errexit

# Modify this line as needed for your package manager (pip, poetry, etc.)
pip install -r requirements.txt

#downloading bltk stopwords and punkt
python -c "import nltk; nltk.download('stopwords')"
python -c "import nltk; nltk.download('punkt')"

# Convert static asset files
python hatespeech/manage.py collectstatic --no-input

# Apply any outstanding database migrations
python hatespeech/manage.py migrate