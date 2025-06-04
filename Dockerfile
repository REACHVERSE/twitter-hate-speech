# Use official Python image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy project files
COPY . /app/

RUN chmod +x build.sh

# Run the app
CMD ["gunicorn", "hatespeech.asgi:application", "-k", "uvicorn.workers.UvicornWorker", "--host", "0.0.0.0", "--port", "8000"]
