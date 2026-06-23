from .base import *  # noqa: F401,F403

SECRET_KEY = os.environ.get(  # noqa: F405
    'dev_SECRET_KEY',
    'dev-secret-key-change-in-production',
)

DATABASES = {
    'default': env_db_config('dev'),  # noqa: F405
}

DEBUG = os.environ.get('DJANGO_DEBUG', 'True').lower() == 'true'  # noqa: F405

ALLOWED_HOSTS = [
    host.strip()
    for host in os.environ.get(  # noqa: F405
        'ALLOWED_HOSTS',
        'localhost,127.0.0.1',
    ).split(',')
    if host.strip()
]

SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
