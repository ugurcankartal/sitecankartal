"""
WSGI config for portfolio project.
Production WSGI entry point for Gunicorn.

Usage:
    gunicorn portfolio.wsgi:application --bind 127.0.0.1:8000
"""
import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'portfolio.settings.prod')

application = get_wsgi_application()
