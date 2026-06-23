#!/usr/bin/env python
"""Start Gunicorn using prod_port from Django settings / .env."""
import os
import subprocess
import sys

# Always use production settings under Gunicorn (ignore .env DJANGO_SETTINGS_MODULE).
os.environ['DJANGO_SETTINGS_MODULE'] = 'portfolio.settings.prod'

BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
GUNICORN_BIN = os.path.join(os.path.dirname(sys.executable), 'gunicorn')


def main():
    import django

    django.setup()

    from django.conf import settings

    if not os.path.isfile(GUNICORN_BIN):
        print(f'ERROR: gunicorn not found at {GUNICORN_BIN}', file=sys.stderr)
        raise SystemExit(1)

    bind = f'{settings.BIND_HOST}:{settings.PROD_PORT}'
    cmd = [
        GUNICORN_BIN,
        'portfolio.wsgi:application',
        '--bind',
        bind,
        '--workers',
        '3',
        '--timeout',
        '120',
        '--access-logfile',
        '-',
        '--error-logfile',
        '-',
    ]
    print(f'Starting Gunicorn on {bind}', flush=True)
    raise SystemExit(
        subprocess.call(cmd, cwd=BACKEND_DIR, env=os.environ.copy())
    )


if __name__ == '__main__':
    main()
