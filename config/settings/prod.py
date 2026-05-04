"""
Production settings for HealthPortal.
DEBUG is off, WhiteNoise serves static files, security headers enabled.
"""

from .base import *  # noqa
import os

DEBUG = False

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
