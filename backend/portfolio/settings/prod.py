from .base import *  # noqa: F401,F403

SECRET_KEY = os.environ.get('prod_SECRET_KEY')  # noqa: F405
if not SECRET_KEY:
    raise ValueError('prod_SECRET_KEY must be set in .env for production settings')

DATABASES = {
    'default': env_db_config('prod'),  # noqa: F405
}

DEBUG = os.environ.get('prod_DJANGO_DEBUG', 'False').lower() == 'true'  # noqa: F405

ALLOWED_HOSTS = [
    host.strip()
    for host in os.environ.get(  # noqa: F405
        'prod_ALLOWED_HOSTS',
        'cankartal.com,www.cankartal.com',
    ).split(',')
    if host.strip()
]

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_X_FORWARDED_HOST = True
