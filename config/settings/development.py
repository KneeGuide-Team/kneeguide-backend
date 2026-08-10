import os

from .base import *


DEBUG = True
SECRET_KEY = os.getenv("SECRET_KEY", "django-insecure-development-only")
ALLOWED_HOSTS = env_list("DEVELOPMENT_ALLOWED_HOSTS", "127.0.0.1,localhost")

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = env_list(
    "CORS_ALLOWED_ORIGINS",
    "http://localhost:3000,http://127.0.0.1:3000",
)
