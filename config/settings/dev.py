"""
Development settings — DEBUG on, verbose logging, SQLite fallback optional.
"""

from .base import *  # noqa

DEBUG = True

# Show emails in terminal during development instead of sending them
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Verbose logging so we can see everything during development
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "DEBUG",
    },
}

LOGIN_URL = "/accounts/login/"

# Enable DRF browsable API in development
REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"] = [
    "rest_framework.renderers.JSONRenderer",
    "rest_framework.renderers.BrowsableAPIRenderer",
]
