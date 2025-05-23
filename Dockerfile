# Use official Python image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV NLTK_DATA=/usr/share/nltk_data

# Set work directory
WORKDIR /app

# Install dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy project files
COPY . /app/

RUN chmod +x build.sh

COPY nltk_data /usr/share/nltk_data

# Ensure the directory exists
RUN mkdir -p /usr/share/nltk_data && \
    python -m nltk.downloader -d /usr/share/nltk_data punkt wordnet stopwords

# Run collectstatic and migrations if needed
CMD ["gunicorn", "hatespeech.asgi:application", "-k", "uvicorn.workers.UvicornWorker", "--host", "0.0.0.0", "--port", "8000"]
