from .settings import *

DEBUG = True
SECURE_SSL_REDIRECT = False

# Isolated in-memory database for automated tests.
# This must never connect to the production Supabase database.
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
        "CONN_MAX_AGE": 0,
    }
}
