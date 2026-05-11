"""
Production settings for HealthPortal.
DEBUG is off, WhiteNoise serves static files, security headers enabled.
"""

from .base import *  # noqa
import dj_database_url

# Andasy (and most PaaS) provide a single DATABASE_URL env var
# This overrides the individual DB_* settings from base.py
db_from_env = dj_database_url.config(conn_max_age=600)
if db_from_env:
    DATABASES["default"].update(db_from_env)
import os

DEBUG = False

# Session and CSRF configuration for production
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = False
CSRF_COOKIE_SAMESITE = 'Lax'
CSRF_TRUSTED_ORIGINS = ["https://healthportal.andasy.dev"]

# Ensure session cookie domain is set
SESSION_COOKIE_DOMAIN = None  # Use current domain

# ---------------------------------------------------------------------------
# SECURITY
# ---------------------------------------------------------------------------

SECURE_BROWSER_XSS_FILTER        = True
SECURE_CONTENT_TYPE_NOSNIFF      = True
X_FRAME_OPTIONS                   = "DENY"
SECURE_HSTS_SECONDS               = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS    = True
SESSION_COOKIE_SECURE             = True
CSRF_COOKIE_SECURE                = True
CSRF_TRUSTED_ORIGINS = ["https://healthportal.andasy.dev"]
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Allow Andasy subdomain — update once you know your exact URL
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["localhost", "127.0.0.1"])

# ---------------------------------------------------------------------------
# STATIC FILES — WhiteNoise
# ---------------------------------------------------------------------------

MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# ---------------------------------------------------------------------------
# LOGGING — structured, errors visible
# ---------------------------------------------------------------------------

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class":     "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console"],
        "level":    "INFO",
    },
    "loggers": {
        "django": {
            "handlers":  ["console"],
            "level":     "ERROR",
            "propagate": False,
        },
    },
}

# ---------------------------------------------------------------------------
# EMAIL — real SMTP in production
# ---------------------------------------------------------------------------

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
