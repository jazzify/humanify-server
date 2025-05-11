import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "humanify_project.settings.prod")

# Get the Django WSGI application
application = get_wsgi_application()
