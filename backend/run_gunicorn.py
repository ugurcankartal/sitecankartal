#!/usr/bin/env python
"""Start Gunicorn using prod_port from Django settings / .env."""
import os
import subprocess
import sys

# Always use production settings under Gunicorn (ignore .env DJANGO_SETTINGS_MODULE).
os.environ['DJANGO_SETTINGS_MODULE'] = 'portfolio.settings.prod'


def main():
    import django

    django.setup()

    from django.conf import settings

    bind = f'{settings.BIND_HOST}:{settings.PROD_PORT}'
    cmd = [
        'gunicorn',
        'portfolio.wsgi:application',
        '--bind',
        bind,
        '--workers',
        '3',
        '--timeout',
        '120',
    ]
    print(f'Starting Gunicorn on {bind}')
    raise SystemExit(subprocess.call(cmd))


if __name__ == '__main__':
    main()
