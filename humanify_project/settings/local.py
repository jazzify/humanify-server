# ruff: noqa: F403 F405
import socket

from humanify_project.settings.base import *

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
