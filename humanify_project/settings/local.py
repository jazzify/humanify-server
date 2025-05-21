# ruff: noqa: F403 F405
import os
import socket

from humanify_project.settings.base import *

# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("POSTGRES_DB"),
        "USER": os.getenv("POSTGRES_USER"),
        "PASSWORD": os.getenv("POSTGRES_PASSWORD"),
        "HOST": os.getenv("POSTGRES_HOST"),
        "PORT": os.getenv("POSTGRES_PORT"),
    }
}

DEBUG = True
INSTALLED_APPS = [
    *INSTALLED_APPS,
    "debug_toolbar",
]
MIDDLEWARE = [
    *MIDDLEWARE,
    "debug_toolbar.middleware.DebugToolbarMiddleware",
]
# tricks to have debug toolbar when developing with docker
ip = socket.gethostbyname(socket.gethostname())
INTERNAL_IPS = [ip[:-1] + "1"]
