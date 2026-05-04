# ---------------------------------------------------------------------------
# HealthPortal — Production Dockerfile
# Python 3.11 slim base keeps the image small.
# Gunicorn serves the Django app; static files via WhiteNoise.
# ---------------------------------------------------------------------------

FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=config.settings.prod

# Working directory inside container
WORKDIR /app

# Install system dependencies needed by psycopg2
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies first (better Docker layer caching)
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy project source
COPY . .

# Collect static files for WhiteNoise to serve
RUN SECRET_KEY=dummy-build-key \
    ALLOWED_HOSTS=localhost \
    DB_NAME=dummy \
    DB_USER=dummy \
    DB_PASSWORD=dummy \
    DB_HOST=localhost \
    DB_PORT=5432 \
    REDIS_URL=redis://localhost:6379/0 \
    EMAIL_HOST=smtp.gmail.com \
    EMAIL_PORT=587 \
    EMAIL_USE_TLS=True \
    EMAIL_HOST_USER=dummy@dummy.com \
    EMAIL_HOST_PASSWORD=dummy \
    SITE_NAME=HealthPortal \
    python manage.py collectstatic --noinput

# Expose application port
EXPOSE 8000

# Start gunicorn — 2 workers is safe for 4GB RAM
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "2", "--timeout", "120"]
