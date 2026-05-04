web: gunicorn config.wsgi:application --bind [::]:8000 --workers 2 --timeout 120
worker: celery -A config worker --loglevel=info --concurrency=1
