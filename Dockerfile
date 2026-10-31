FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . /app/

# Collect static files during the build
RUN python manage.py collectstatic --noinput

# Start the app
CMD gunicorn shopease_project.wsgi --log-file - --bind 0.0.0.0:8080