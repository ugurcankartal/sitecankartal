"""
WSGI config for portfolio project.
Production WSGI entry point for Gunicorn.

Usage:
    gunicorn portfolio.wsgi:application --bind 127.0.0.1:8000
"""
import os

# Always use production settings under Gunicorn (ignore .env DJANGO_SETTINGS_MODULE).
os.environ['DJANGO_SETTINGS_MODULE'] = 'portfolio.settings.prod'

from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
