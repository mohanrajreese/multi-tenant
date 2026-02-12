from .settings import *

# In-memory database for mathematical property verification
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

# Ensure testing speed by disabling unnecessary middleware if needed
# But for property tests, we want to stay as close to production as possible.

# OTEL and Resilience are part of the test but we can disable OTEL exporters
DEBUG = False 
TESTING = True
