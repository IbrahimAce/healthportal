"""
Celery application configuration for HealthPortal.

Tasks are auto-discovered from each app's tasks.py file.
Broker and result backend are both Redis (configured in base.py).
"""

import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")

app = Celery("healthportal")

# Pull Celery config from Django settings (keys prefixed with CELERY_)
app.config_from_object("django.conf:settings", namespace="CELERY")

# Auto-discover tasks.py in every installed app
app.autodiscover_tasks()
